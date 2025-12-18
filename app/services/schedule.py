from datetime import datetime, timezone
from fastapi import HTTPException
from app.database import supabase


def create_schedule(user_id, subject, start_time, end_time):

    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        raise HTTPException(status_code=400, detail="Invalid datetime values")

    start_time = start_time.astimezone(timezone.utc)
    end_time = end_time.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    if start_time <= now:
        raise HTTPException(
            status_code=400,
            detail="Start time must be in the future"
        )

    # Overlap prevention
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

    supabase.table("schedules").insert({
        "user_id": user_id,
        "subject": subject.strip().upper(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "reminder_sent": False
    }).execute()
