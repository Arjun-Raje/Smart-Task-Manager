from datetime import datetime
from models.task import Task

EFFORT_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3
}

def score_task(task: Task) -> float:
    score = 0

    # Deadline urgency
    if task.deadline:
        hours_until_due = (task.deadline - datetime.utcnow()).total_seconds() / 3600
        if hours_until_due > 0:
            score += max(0, 100 - hours_until_due)
        else:
            score += 100  # overdue

    # Effort weighting
    score += EFFORT_WEIGHT.get(task.effort, 0) * 10

    return score


def rank_tasks(tasks: list[Task]) -> list[Task]:
    incomplete = [t for t in tasks if not t.completed]
    return sorted(incomplete, key=score_task, reverse=True)
