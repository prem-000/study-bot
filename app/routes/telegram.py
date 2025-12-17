from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import re
from app.models import TelegramScheduleRequest
from app.services.schedule import create_schedule
from app.database import supabase

router = APIRouter(prefix="/telegram", tags=["Telegram"])
@router.post("/schedule")
@router.post("/schedule")
def create_from_telegram(data: TelegramScheduleRequest):

    try:
        text = data.text.strip().lower()

        # Parse: subject start-end
        match = re.fullmatch(
            r"([a-zA-Z ]+)\s+(\d{1,2})(?::(\d{2}))?-(\d{1,2})(?::(\d{2}))?",
            text
        )

        if not match:
            raise ValueError("Use format: subject start-end (e.g. aiml 6-7)")

        subject = match.group(1).strip()

        sh = int(match.group(2))
        sm = int(match.group(3) or 0)
        eh = int(match.group(4))
        em = int(match.group(5) or 0)

        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)

        start_time = now.replace(
            hour=sh,
            minute=sm,
            second=0,
            microsecond=0
        )

        end_time = now.replace(
            hour=eh,
            minute=em,
            second=0,
            microsecond=0
        )

        # Handle crossing midnight
        if end_time <= start_time:
            end_time += timedelta(days=1)

        # Fetch user
        user = (
            supabase.table("app_users")
            .select("id")
            .eq("telegram_id", data.telegram_id)
            .execute()
        )

        if not user.data:
            raise ValueError("User not registered")

        user_id = user.data[0]["id"]

        # Insert schedule (reuse existing logic)
        create_schedule(
            user_id=user_id,
            subject=subject,
            start_time=start_time,
            end_time=end_time
        )


        return {
            "message": f"✅ Schedule saved\n\n{subject.upper()} "
                       f"{start_time.strftime('%I:%M %p')} - "
                       f"{end_time.strftime('%I:%M %p')}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
