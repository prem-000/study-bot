import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from app.database import supabase
from app.services.schedule import create_schedule

router = APIRouter(prefix="/telegram", tags=["Telegram"])


# ---------- Request Model ----------
class TelegramScheduleRequest(BaseModel):
    telegram_id: int
    text: str


# ---------- Helpers ----------
def to_24h(hour: int, ampm: str | None) -> int:
    if not ampm:
        return hour
    ampm = ampm.lower()
    if ampm == "pm" and hour != 12:
        return hour + 12
    if ampm == "am" and hour == 12:
        return 0
    return hour


# ---------- Endpoint ----------
@router.post("/schedule")
def create_from_telegram(data: TelegramScheduleRequest):
    try:
        text = data.text.strip().lower()

        # Supported formats:
        # aiml 6-7
        # aiml 6pm-7pm
        # aiml 6:30pm - 7:45pm
        # aiml 18-19
        match = re.fullmatch(
            r"([a-zA-Z ]+)\s+"
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*-\s*"
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
            text
        )

        if not match:
            raise ValueError(
                "Invalid format. Use: subject start-end (e.g. aiml 6-7 or aiml 6pm-7pm)"
            )

        subject = match.group(1).strip()

        sh = int(match.group(2))
        sm = int(match.group(3) or 0)
        s_ampm = match.group(4)

        eh = int(match.group(5))
        em = int(match.group(6) or 0)
        e_ampm = match.group(7)

        sh = to_24h(sh, s_ampm)
        eh = to_24h(eh, e_ampm)

        now = datetime.now(timezone.utc)

        start_time = now.replace(
            hour=sh, minute=sm, second=0, microsecond=0
        )
        end_time = now.replace(
            hour=eh, minute=em, second=0, microsecond=0
        )

        # Handle crossing midnight
        if end_time <= start_time:
            end_time += timedelta(days=1)

        # ---------- Fetch user ----------
        user = (
            supabase.table("app_users")
            .select("id")
            .eq("telegram_id", data.telegram_id)
            .execute()
        )

        if not user.data:
            raise ValueError("User not registered")

        user_id = user.data[0]["id"]

        # ---------- Create schedule ----------
        create_schedule(
            user_id=user_id,
            subject=subject,
            start_time=start_time,
            end_time=end_time
        )

        return {
            "message": (
                "✅ Schedule saved\n\n"
                f"{subject.upper()} "
                f"{start_time.strftime('%I:%M %p')} - "
                f"{end_time.strftime('%I:%M %p')}"
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
