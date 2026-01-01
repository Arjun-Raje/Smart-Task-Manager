from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.task import Task
from models.user import User
from services.email_service import send_deadline_reminder


# Track which tasks have already had reminders sent (in-memory for simplicity)
# In production, you'd want to store this in the database
sent_reminders: set[int] = set()


def check_upcoming_deadlines():
    """Check for tasks with deadlines in the next hour and send reminders."""
    print("[Scheduler] Checking for upcoming deadlines...")

    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        one_hour_from_now = now + timedelta(hours=1)

        # Find tasks that:
        # 1. Have a deadline between now and 1 hour from now
        # 2. Are not completed
        # 3. Haven't had a reminder sent yet
        upcoming_tasks = db.query(Task).filter(
            Task.deadline.isnot(None),
            Task.deadline > now,
            Task.deadline <= one_hour_from_now,
            Task.completed == False,
            Task.id.notin_(sent_reminders) if sent_reminders else True
        ).all()

        print(f"[Scheduler] Found {len(upcoming_tasks)} tasks with upcoming deadlines")

        for task in upcoming_tasks:
            # Skip if already sent
            if task.id in sent_reminders:
                continue

            # Get the task owner's email
            owner = db.query(User).filter(User.id == task.owner_id).first()
            if not owner:
                continue

            # Send reminder email
            success = send_deadline_reminder(
                recipient_email=owner.email,
                task_title=task.title,
                task_id=task.id,
                deadline=task.deadline
            )

            if success:
                sent_reminders.add(task.id)
                print(f"[Scheduler] Sent deadline reminder for task {task.id} to {owner.email}")

    except Exception as e:
        print(f"[Scheduler] Error checking deadlines: {str(e)}")
    finally:
        db.close()


def clear_old_reminders():
    """Clean up sent_reminders for tasks that are past their deadline."""
    print("[Scheduler] Cleaning up old reminder records...")

    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        # Find tasks whose deadlines have passed
        tasks_to_clear = []
        for task_id in sent_reminders:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task or (task.deadline and task.deadline < now):
                tasks_to_clear.append(task_id)

        for task_id in tasks_to_clear:
            sent_reminders.discard(task_id)

        if tasks_to_clear:
            print(f"[Scheduler] Cleared {len(tasks_to_clear)} old reminder records")

    except Exception as e:
        print(f"[Scheduler] Error clearing old reminders: {str(e)}")
    finally:
        db.close()


# Global scheduler instance
scheduler: BackgroundScheduler | None = None


def start_scheduler():
    """Start the background scheduler."""
    global scheduler

    if scheduler is not None:
        print("[Scheduler] Scheduler already running")
        return

    scheduler = BackgroundScheduler()

    # Check for upcoming deadlines every 5 minutes
    scheduler.add_job(
        check_upcoming_deadlines,
        trigger=IntervalTrigger(minutes=5),
        id="check_deadlines",
        name="Check for upcoming task deadlines",
        replace_existing=True
    )

    # Clean up old reminder records every hour
    scheduler.add_job(
        clear_old_reminders,
        trigger=IntervalTrigger(hours=1),
        id="clear_reminders",
        name="Clear old reminder records",
        replace_existing=True
    )

    scheduler.start()
    print("[Scheduler] Background scheduler started")

    # Run an initial check
    check_upcoming_deadlines()


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler

    if scheduler:
        scheduler.shutdown()
        scheduler = None
        print("[Scheduler] Background scheduler stopped")
