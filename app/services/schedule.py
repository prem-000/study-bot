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


from datetime import datetime

def create_schedule(user_id, subject, start_time, end_time):

    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()

    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    supabase.table("schedules").insert({
        "user_id": user_id,
        "subject": subject,
        "start_time": start_time,
        "end_time": end_time
    }).execute()


