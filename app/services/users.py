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

    user = (
        supabase
        .table("app_users")
        .insert({"telegram_id": telegram_id})
        .execute()
    )

    return user.data[0]["id"]
