from fastapi import APIRouter
from app.models import ScheduleCreate
from app.services.schedule import get_or_create_user, create_schedule

router = APIRouter()

@router.post("/schedule")
def add_schedule(data: ScheduleCreate):
    user_id = get_or_create_user(data.telegram_id)

    create_schedule(
        user_id,
        data.subject,
        data.start_time,
        data.end_time
    )

    return {"message": "Schedule saved"}
