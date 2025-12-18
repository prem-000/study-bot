from app.database import supabase

def get_or_create_user(telegram_id: int) -> str:
    res = (
        supabase
        .table("app_users")
        .select("id")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    if res.data:
        return res.data[0]["id"]

    user = supabase.table("app_users").insert({
        "telegram_id": telegram_id
    }).execute()

    return user.data[0]["id"]


from datetime import datetime, timezone
from fastapi import HTTPException
from app.database import supabase


def create_schedule(user_id, subject, start_time, end_time):

    # Ensure datetime objects
    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        raise HTTPException(status_code=400, detail="Invalid datetime values")

    # Force UTC
    start_time = start_time.astimezone(timezone.utc)
    end_time = end_time.astimezone(timezone.utc)

    # Prevent past schedules
    now = datetime.now(timezone.utc)
    if start_time <= now:
        raise HTTPException(
            status_code=400,
            detail="Start time must be in the future"
        )

    # Prevent overlapping schedules
    conflict = (
        supabase
        .table("schedules")
        .select("id")
        .eq("user_id", user_id)
        .lt("start_time", end_time.isoformat())
        .gt("end_time", start_time.isoformat())
        .execute()
    )

    if conflict.data:
        raise HTTPException(
            status_code=400,
            detail="Time conflict with an existing schedule"
        )

    # Insert schedule
    supabase.table("schedules").insert({
        "user_id": user_id,
        "subject": subject,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "reminder_sent": False
    }).execute()
