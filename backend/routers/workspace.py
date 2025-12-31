import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from models.user import User
from models.task import Task
from models.task_note import TaskNote
from models.task_attachment import TaskAttachment
from models.task_summary import TaskSummary
from models.task_resource import TaskResource
from models.task_share import TaskShare
from db.deps import get_db
from schemas.task_note import TaskNoteUpdate, TaskNoteResponse
from schemas.task_attachment import TaskAttachmentResponse
from schemas.task_summary import TaskSummaryResponse
from schemas.task_resource import TaskResourceResponse
from config import UPLOAD_DIR, ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE
from services.ai_service import generate_task_summary, extract_pdf_text
from services.resource_service import find_resources

router = APIRouter(prefix="/tasks/{task_id}/workspace", tags=["Workspace"])


def get_user_task(task_id: int, db: Session, current_user: User, require_edit: bool = False) -> Task:
    """Helper to verify task ownership or shared access."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Owner has full access
    if task.owner_id == current_user.id:
        return task

    # Check if shared with user
    share = db.query(TaskShare).filter(
        TaskShare.task_id == task_id,
        TaskShare.shared_with_id == current_user.id
    ).first()

    if not share:
        raise HTTPException(status_code=404, detail="Task not found")

    if require_edit and share.permission != "edit":
        raise HTTPException(status_code=403, detail="You don't have edit permission")

    return task


# ============ NOTES ENDPOINTS ============

@router.get("/notes", response_model=TaskNoteResponse | None)
def get_task_notes(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user)
    note = db.query(TaskNote).filter(TaskNote.task_id == task_id).first()
    return note


@router.put("/notes", response_model=TaskNoteResponse)
def update_task_notes(
    task_id: int,
    note_data: TaskNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user, require_edit=True)

    note = db.query(TaskNote).filter(TaskNote.task_id == task_id).first()

    if note:
        note.content = note_data.content
    else:
        note = TaskNote(task_id=task_id, content=note_data.content)
        db.add(note)

    db.commit()
    db.refresh(note)
    return note


# ============ ATTACHMENTS ENDPOINTS ============

@router.get("/attachments", response_model=list[TaskAttachmentResponse])
def get_task_attachments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user)
    attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).all()
    return attachments


@router.post("/attachments", response_model=TaskAttachmentResponse)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user, require_edit=True)

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Allowed types: PDF, PNG, JPG, GIF, WEBP"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Generate unique stored filename
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    stored_filename = f"{uuid.uuid4()}{ext}"

    # Create task-specific directory
    task_upload_dir = UPLOAD_DIR / str(task_id)
    task_upload_dir.mkdir(exist_ok=True)

    # Save file
    file_path = task_upload_dir / stored_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    attachment = TaskAttachment(
        task_id=task_id,
        filename=file.filename or "unnamed",
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_size=file_size
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user)

    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id,
        TaskAttachment.task_id == task_id
    ).first()

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    file_path = UPLOAD_DIR / str(task_id) / attachment.stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.content_type
    )


@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_user_task(task_id, db, current_user, require_edit=True)

    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id,
        TaskAttachment.task_id == task_id
    ).first()

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Delete file from disk
    file_path = UPLOAD_DIR / str(task_id) / attachment.stored_filename
    if file_path.exists():
        os.remove(file_path)

    # Delete database record
    db.delete(attachment)

    # Clear cached summary and resources since attachments changed
    db.query(TaskSummary).filter(TaskSummary.task_id == task_id).delete()
    db.query(TaskResource).filter(TaskResource.task_id == task_id).delete()
    print(f"[Attachment Delete] Cleared cached summary and resources for task {task_id}")

    db.commit()

    return {"message": "Attachment deleted", "summary_cleared": True, "resources_cleared": True}


# ============ AI SUMMARY ENDPOINTS ============

@router.get("/summary")
def get_saved_summary(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the saved AI summary for a task."""
    get_user_task(task_id, db, current_user)

    summary = db.query(TaskSummary).filter(TaskSummary.task_id == task_id).first()

    if not summary:
        return None

    return {
        "summary": summary.summary,
        "key_points": summary.key_points,
        "concepts": summary.concepts,
        "action_items": summary.action_items,
        "study_tips": summary.study_tips,
        "error": False,
        "updated_at": summary.updated_at.isoformat() if summary.updated_at else None
    }


@router.delete("/summary")
def delete_summary(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the saved AI summary for a task."""
    get_user_task(task_id, db, current_user, require_edit=True)

    deleted = db.query(TaskSummary).filter(TaskSummary.task_id == task_id).delete()
    db.commit()

    print(f"[Summary Delete] Deleted {deleted} summary for task {task_id}")
    return {"deleted": deleted > 0}


@router.post("/summary/generate")
def generate_and_save_summary(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a FRESH AI summary - always reads current attachments and notes."""
    task = get_user_task(task_id, db, current_user, require_edit=True)

    # STEP 1: Delete any existing summary first
    db.query(TaskSummary).filter(TaskSummary.task_id == task_id).delete()
    db.commit()
    print(f"[Summary Generate] Deleted old summary for task {task_id}")

    # STEP 2: Get fresh notes
    note = db.query(TaskNote).filter(TaskNote.task_id == task_id).first()
    notes_content = note.content if note else ""
    print(f"[Summary Generate] Notes content: {len(notes_content)} chars")

    # STEP 3: Get current attachments from database
    attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).all()

    print(f"[Summary Generate] === CURRENT ATTACHMENTS FOR TASK {task_id} ===")
    print(f"[Summary Generate] Found {len(attachments)} attachments in database")

    # Build attachment data - only include files that exist on disk
    attachment_data = []
    for att in attachments:
        file_path = UPLOAD_DIR / str(task_id) / att.stored_filename
        exists = file_path.exists()
        print(f"[Summary Generate]   - {att.filename} | stored: {att.stored_filename} | exists: {exists}")

        if exists:
            attachment_data.append({
                "task_id": att.task_id,
                "stored_filename": att.stored_filename,
                "filename": att.filename,
                "content_type": att.content_type
            })

    print(f"[Summary Generate] Processing {len(attachment_data)} valid attachments")

    # STEP 4: Generate fresh summary
    result = generate_task_summary(task.title, notes_content, attachment_data)

    # If there was an error, return it without saving
    if result.get("error"):
        return result

    # STEP 5: Save the new summary
    new_summary = TaskSummary(
        task_id=task_id,
        summary=result.get("summary", ""),
        key_points=result.get("key_points", []),
        concepts=result.get("concepts", []),
        action_items=result.get("action_items", []),
        study_tips=result.get("study_tips", [])
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    result["updated_at"] = new_summary.updated_at.isoformat() if new_summary.updated_at else None
    print(f"[Summary Generate] New summary saved for task {task_id}")

    return result


# ============ RESOURCES ENDPOINTS ============

@router.get("/resources", response_model=list[TaskResourceResponse])
def get_saved_resources(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get saved resources for a task."""
    get_user_task(task_id, db, current_user)

    resources = db.query(TaskResource).filter(
        TaskResource.task_id == task_id
    ).order_by(TaskResource.created_at.desc()).all()

    return resources


@router.delete("/resources")
def delete_resources(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all saved resources for a task."""
    get_user_task(task_id, db, current_user, require_edit=True)

    deleted = db.query(TaskResource).filter(TaskResource.task_id == task_id).delete()
    db.commit()

    print(f"[Resources Delete] Deleted {deleted} resources for task {task_id}")
    return {"deleted": deleted}


@router.post("/resources/generate")
def generate_resources(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate FRESH resource suggestions - always reads current attachments and notes."""
    task = get_user_task(task_id, db, current_user, require_edit=True)

    # STEP 1: Delete any existing resources first
    db.query(TaskResource).filter(TaskResource.task_id == task_id).delete()
    db.commit()
    print(f"[Resources Generate] Deleted old resources for task {task_id}")

    # STEP 2: Get fresh notes
    note = db.query(TaskNote).filter(TaskNote.task_id == task_id).first()
    notes_content = note.content if note else ""
    print(f"[Resources Generate] Notes content: {len(notes_content)} chars")

    # STEP 3: Get ALL attachments and extract text from PDFs
    pdf_content = ""
    all_attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).all()

    print(f"[Resources Generate] === ALL ATTACHMENTS FOR TASK {task_id} ===")
    print(f"[Resources Generate] Found {len(all_attachments)} total attachments in database")

    pdf_attachments = [a for a in all_attachments if a.content_type == "application/pdf"]
    print(f"[Resources Generate] Found {len(pdf_attachments)} PDF attachments")

    for att in pdf_attachments[:5]:  # Process up to 5 PDFs
        file_path = UPLOAD_DIR / str(task_id) / att.stored_filename
        exists = file_path.exists()
        print(f"[Resources Generate]   - {att.filename} | stored: {att.stored_filename} | exists: {exists}")

        if exists:
            extracted = extract_pdf_text(file_path)
            print(f"[Resources Generate]   Extraction result: {len(extracted) if extracted else 0} chars")
            print(f"[Resources Generate]   First 200 chars: {extracted[:200] if extracted else 'None'}...")

            # Include content even if it starts with [ - just log a warning
            if extracted:
                if extracted.startswith("["):
                    print(f"[Resources Generate]   WARNING: PDF extraction returned message: {extracted[:100]}")
                else:
                    pdf_content += f"\n\n=== PDF: {att.filename} ===\n{extracted[:12000]}"
                    print(f"[Resources Generate]   Added {min(len(extracted), 12000)} chars from {att.filename}")

    print(f"[Resources Generate] Total PDF content: {len(pdf_content)} chars")

    # STEP 4: Find fresh resources based on current content
    # Use task title as fallback if no notes/PDF content but there are image attachments
    has_any_attachments = len(all_attachments) > 0
    has_text_content = bool(notes_content.strip()) or bool(pdf_content.strip())

    print(f"[Resources Generate] has_any_attachments: {has_any_attachments}, has_text_content: {has_text_content}")

    # If we have attachments but no extractable text, use task title as content hint
    effective_notes = notes_content
    if has_any_attachments and not has_text_content and task.title:
        effective_notes = f"Topic: {task.title}"
        print(f"[Resources Generate] Using task title as content hint: {task.title}")

    resources = find_resources(
        task_title=task.title,
        notes_content=effective_notes,
        pdf_content=pdf_content,
        num_resources=5
    )

    if not resources:
        return {"resources": [], "error": "Could not find relevant resources. Please add notes or upload PDFs with readable text."}

    # STEP 5: Save new resources
    saved_resources = []
    for r in resources:
        resource = TaskResource(
            task_id=task_id,
            title=r.get("title", ""),
            url=r.get("url", ""),
            description=r.get("description", ""),
            source=r.get("source", "")
        )
        db.add(resource)
        saved_resources.append(resource)

    db.commit()

    for r in saved_resources:
        db.refresh(r)

    print(f"[Resources Generate] Saved {len(saved_resources)} new resources for task {task_id}")

    return {
        "resources": [
            {
                "id": r.id,
                "task_id": r.task_id,
                "title": r.title,
                "url": r.url,
                "description": r.description,
                "source": r.source,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in saved_resources
        ],
        "error": None
    }
