import asyncio
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.devices.dao import DeviceDAO
from src.replacement_suggestions.dao import ReplacementSuggestionDAO

async def generate_expired_warranty_suggestions():
    today = date.today()
    devices = await DeviceDAO.find_all()
    expired = [d for d in devices if d.warranty_end and d.warranty_end <= today]
    for device in expired:
        part_type_id = device.type.part_type_id
        existing = await ReplacementSuggestionDAO.find_all(
            part_type_id=part_type_id,
            date_from=today,
            date_to=today
        )
        if existing:
            continue

        await ReplacementSuggestionDAO.create(
            part_type_id=part_type_id,
            forecast_replacement_date=today,
            generated_by="system:expired_warranty",
            comments=f"Auto-generated for device {device.id} after warranty_end={device.warranty_end}",
            status="pending"
        )

def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    trigger = CronTrigger(hour=0, minute=10)
    scheduler.add_job(
        lambda: asyncio.create_task(generate_expired_warranty_suggestions()),
        trigger=trigger,
        id="expired_warranty_job",
        replace_existing=True
    )
    scheduler.start()
    return scheduler
