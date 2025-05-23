from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as router_auth
from src.part_types.router import router as router_part_types
from src.device_types.router import router as router_device_types
from src.locations.router import router as router_locations
from src.devices.router import router as router_devices
from src.movements.router import router as router_movements
from src.inventory_events.router import router as router_inventory_events
from src.inventory_items.router import router as router_inventory_items
from src.maintenance_tasks.router import router as router_maintenance
from src.failure_records.router import router as router_failure
from src.replacement_suggestions.router import router as router_replacement_suggestions
from src.write_off_reports.router import router as router_reports
from src.analytics.router import router as router_analytics
from src.users.router import router as router_users
from src.stats.router import router as router_stats
from src.tasks.warranty_suggestions import start_scheduler
from src.exception_handlers import add_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

# Add exception handlers
# add_exception_handlers(app)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_part_types)
app.include_router(router_device_types)
app.include_router(router_locations)
app.include_router(router_devices)
app.include_router(router_movements)
app.include_router(router_inventory_events)
app.include_router(router_inventory_items)
app.include_router(router_maintenance)
app.include_router(router_failure)
app.include_router(router_replacement_suggestions)
app.include_router(router_reports)
app.include_router(router_analytics)
app.include_router(router_stats)

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
