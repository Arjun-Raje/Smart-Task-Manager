from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.deps import get_db
from auth.deps import get_current_user
from models.user import User
from models.task import Task
from models.task_share import TaskShare
from schemas.task_share import TaskShareCreate, TaskShareResponse, SharedTaskResponse

router = APIRouter(tags=["Share"])


@router.post("/tasks/{task_id}/share", response_model=TaskShareResponse)
def share_task(
    task_id: int,
    share_data: TaskShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share a task with another user by their email."""
    # Verify task exists and user owns it
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Find user to share with
    target_user = db.query(User).filter(User.email == share_data.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Can't share with yourself
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share task with yourself")

    # Check if already shared
    existing_share = db.query(TaskShare).filter(
        TaskShare.task_id == task_id,
        TaskShare.shared_with_id == target_user.id
    ).first()
    if existing_share:
        raise HTTPException(status_code=400, detail="Task already shared with this user")

    # Validate permission
    if share_data.permission not in ["view", "edit"]:
        raise HTTPException(status_code=400, detail="Permission must be 'view' or 'edit'")

    # Create share
    new_share = TaskShare(
        task_id=task_id,
        shared_with_id=target_user.id,
        permission=share_data.permission
    )
    db.add(new_share)
    db.commit()
    db.refresh(new_share)

    return TaskShareResponse(
        id=new_share.id,
        task_id=new_share.task_id,
        shared_with_email=target_user.email,
        permission=new_share.permission,
        shared_at=new_share.shared_at
    )


@router.get("/tasks/{task_id}/shares", response_model=list[TaskShareResponse])
def get_task_shares(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users a task is shared with (only task owner can view)."""
    # Verify task exists and user owns it
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    shares = db.query(TaskShare).filter(TaskShare.task_id == task_id).all()

    result = []
    for share in shares:
        user = db.query(User).filter(User.id == share.shared_with_id).first()
        result.append(TaskShareResponse(
            id=share.id,
            task_id=share.task_id,
            shared_with_email=user.email if user else "Unknown",
            permission=share.permission,
            shared_at=share.shared_at
        ))

    return result


@router.delete("/tasks/{task_id}/share/{share_id}")
def revoke_share(
    task_id: int,
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a task share (only task owner can revoke)."""
    # Verify task exists and user owns it
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    share = db.query(TaskShare).filter(
        TaskShare.id == share_id,
        TaskShare.task_id == task_id
    ).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    db.delete(share)
    db.commit()

    return {"message": "Share revoked"}


@router.get("/tasks/{task_id}/my-permission")
def get_my_permission(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's permission level for a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Owner has full access
    if task.owner_id == current_user.id:
        owner = db.query(User).filter(User.id == task.owner_id).first()
        return {
            "permission": "owner",
            "owner_email": owner.email if owner else "Unknown",
            "is_owner": True
        }

    # Check if shared with user
    share = db.query(TaskShare).filter(
        TaskShare.task_id == task_id,
        TaskShare.shared_with_id == current_user.id
    ).first()

    if not share:
        raise HTTPException(status_code=404, detail="Task not found")

    owner = db.query(User).filter(User.id == task.owner_id).first()
    return {
        "permission": share.permission,
        "owner_email": owner.email if owner else "Unknown",
        "is_owner": False
    }


@router.get("/shared-with-me", response_model=list[SharedTaskResponse])
def get_shared_with_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks shared with the current user."""
    shares = db.query(TaskShare).filter(
        TaskShare.shared_with_id == current_user.id
    ).all()

    result = []
    for share in shares:
        task = db.query(Task).filter(Task.id == share.task_id).first()
        if task:
            owner = db.query(User).filter(User.id == task.owner_id).first()
            result.append(SharedTaskResponse(
                id=task.id,
                title=task.title,
                deadline=task.deadline,
                effort=task.effort,
                completed=task.completed,
                owner_email=owner.email if owner else "Unknown",
                permission=share.permission,
                shared_at=share.shared_at
            ))

    return result
