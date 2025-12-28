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
from db.deps import get_db
from schemas.task_note import TaskNoteUpdate, TaskNoteResponse
from schemas.task_attachment import TaskAttachmentResponse
from schemas.task_summary import TaskSummaryResponse
from config import UPLOAD_DIR, ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE
from services.ai_service import generate_task_summary

router = APIRouter(prefix="/tasks/{task_id}/workspace", tags=["Workspace"])


def get_user_task(task_id: int, db: Session, current_user: User) -> Task:
    """Helper to verify task ownership."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
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
    get_user_task(task_id, db, current_user)

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
    get_user_task(task_id, db, current_user)

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
    get_user_task(task_id, db, current_user)

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
    db.commit()

    return {"message": "Attachment deleted"}


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


@router.post("/summary/generate")
def generate_and_save_summary(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new AI summary and save it to the database."""
    task = get_user_task(task_id, db, current_user)

    # Get the notes for this task
    note = db.query(TaskNote).filter(TaskNote.task_id == task_id).first()
    notes_content = note.content if note else ""

    # Get attachments for this task
    attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).all()

    # Convert attachments to dict format for AI service
    attachment_data = [
        {
            "task_id": att.task_id,
            "stored_filename": att.stored_filename,
            "filename": att.filename,
            "content_type": att.content_type
        }
        for att in attachments
    ]

    # Generate summary using AI (notes + attachments)
    result = generate_task_summary(task.title, notes_content, attachment_data)

    # If there was an error, return it without saving
    if result.get("error"):
        return result

    # Save or update the summary in the database
    existing_summary = db.query(TaskSummary).filter(TaskSummary.task_id == task_id).first()

    if existing_summary:
        existing_summary.summary = result.get("summary", "")
        existing_summary.key_points = result.get("key_points", [])
        existing_summary.concepts = result.get("concepts", [])
        existing_summary.action_items = result.get("action_items", [])
        existing_summary.study_tips = result.get("study_tips", [])
    else:
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

    # Return the result with updated_at timestamp
    result["updated_at"] = None
    if existing_summary:
        db.refresh(existing_summary)
        result["updated_at"] = existing_summary.updated_at.isoformat() if existing_summary.updated_at else None

    return result
