from fastapi import APIRouter
from app.services.reminders import get_due_reminders, mark_reminder_sent

router = APIRouter()

@router.get("/due-reminders")
def due_reminders():
    return get_due_reminders()

@router.post("/mark-reminded/{schedule_id}")
def mark_reminded(schedule_id: str):
    mark_reminder_sent(schedule_id)
    return {"status": "ok"}
