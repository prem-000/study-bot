from datetime import datetime, timezone
from app.database import supabase


def get_due_reminders():
    now = datetime.now(timezone.utc).isoformat()

    res = (
        supabase
        .table("schedules")
        .select("id, subject, start_time, app_users(telegram_id)")
        .lte("start_time", now)
        .eq("reminder_sent", False)
        .execute()
    )

    return res.data


def mark_reminder_sent(schedule_id: str):
    supabase.table("schedules").update({
        "reminder_sent": True,
        "reminder_sent_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", schedule_id).eq("reminder_sent", False).execute()
