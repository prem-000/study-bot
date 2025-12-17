from pydantic import BaseModel
from datetime import datetime

class ScheduleCreate(BaseModel):
    telegram_id: int
    subject: str
    start_time: datetime
    end_time: datetime
