from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.schedule import router as schedule_router
from app.routes.reminders import router as reminders_router

app = FastAPI(title="Study Bot Backend")

app.include_router(health_router)
app.include_router(schedule_router)
app.include_router(reminders_router)
