from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import re
from app.models import TelegramScheduleRequest
from app.services.schedule import create_schedule
from app.database import supabase

router = APIRouter(prefix="/telegram", tags=["Telegram"])
@router.post("/schedule")
def create_from_telegram(data: TelegramScheduleRequest):
    """
    Expected text format:
    subject start-end
    Example: aiml 6-7
    """

    text = data.text.strip().lower()

    # regex: subject + start-end
    match = re.match(r"([a-zA-Z ]+)\s+(\d{1,2})(?::(\d{2}))?-(\d{1,2})(?::(\d{2}))?", text)

    if not match:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Use: subject start-end (e.g. aiml 6-7)"
        )

    subject = match.group(1).strip()

    sh = int(match.group(2))
    sm = int(match.group(3) or 0)
    eh = int(match.group(4))
    em = int(match.group(5) or 0)

    today = datetime.now().astimezone()
    start_time = today.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end_time = today.replace(hour=eh, minute=em, second=0, microsecond=0)

    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    # get user
    user = (
        supabase.table("app_users")
        .select("id")
        .eq("telegram_id", data.telegram_id)
        .execute()
    )

    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user.data[0]["id"]

    # reuse existing schedule logic
    create_schedule(
        user_id=user_id,
        subject=subject,
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat()
    )

    return {
        "message": f"✅ Schedule saved\n\n{subject.upper()} {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
    }
