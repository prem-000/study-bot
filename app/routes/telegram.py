import re
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta

from app.models import TelegramScheduleRequest
from app.services.schedule import create_schedule
from app.database import supabase

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/schedule")
def create_from_telegram(data: TelegramScheduleRequest):
    try:
        text = data.text.strip().lower()

        # Format: subject start-end (24h or logical next slot)
        match = re.fullmatch(
            r"([a-zA-Z ]+)\s+(\d{1,2})(?::(\d{2}))?-(\d{1,2})(?::(\d{2}))?",
            text
        )

        if not match:
            raise ValueError("Use format: subject start-end (e.g. pd 1-2 or pd 18-19)")

        subject = match.group(1).strip()

        sh = int(match.group(2))
        sm = int(match.group(3) or 0)
        eh = int(match.group(4))
        em = int(match.group(5) or 0)

        now = datetime.now(timezone.utc)

        # Create tentative times (today)
        start_time = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end_time = now.replace(hour=eh, minute=em, second=0, microsecond=0)

        # If end <= start, assume crossing midnight
        if end_time <= start_time:
            end_time += timedelta(days=1)

        # 🔑 NEXT UPCOMING TIME LOGIC
        # If start_time already passed → schedule for next day
        # If AM/PM not specified, assume next upcoming slot
        if start_time <= now:
            # Try PM first (add 12 hours)
            start_time_pm = start_time + timedelta(hours=12)
            end_time_pm = end_time + timedelta(hours=12)

            if start_time_pm > now:
                start_time = start_time_pm
                end_time = end_time_pm
            else:
                # Otherwise, schedule tomorrow
                start_time += timedelta(days=1)
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

        # Store schedule
        create_schedule(
            user_id=user_id,
            subject=subject,
            start_time=start_time,
            end_time=end_time
        )

        return {
            "message": (
                "📘 *STUDY SCHEDULE SAVED*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                f"📚 *Subject* : {subject.upper()}\n"
                f"⏰ *Time*    : {start_time.strftime('%I:%M %p')} – "
                f"{end_time.strftime('%I:%M %p')}\n"
                f"📅 *Date*    : {start_time.strftime('%d %b %Y')}\n"
                "━━━━━━━━━━━━━━━━\n\n"
                "🔥 Stay focused. No excuses."
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
