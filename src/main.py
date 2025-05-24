from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from prometheus_client import Gauge, Counter
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.router import router as router_auth
from src.part_types.router import router as router_part_types
from src.device_types.router import router as router_device_types
from src.locations.router import router as router_locations
from src.devices.router import router as router_devices
from src.movements.router import (
    router as router_movements,
    admin_router as router_movements_admin,
)
from src.inventory_events.router import router as router_inventory_events
from src.inventory_items.router import router as router_inventory_items
from src.maintenance_tasks.router import router as router_maintenance
from src.failure_records.router import router as router_failure
from src.replacement_suggestions.router import router as router_replacement_suggestions
from src.write_off_reports.router import router as router_reports
from src.analytics.router import router as router_analytics
from src.users.router import router as router_users
from src.stats.router import router as router_stats
from src.adminpanel.views import (
    UserAdmin,
    DeviceAdmin,
    DeviceTypeAdmin,
    LocationAdmin,
    PartTypeAdmin,
    FailureRecordAdmin,
    MaintenanceTaskAdmin,
    InventoryItemAdmin,
    InventoryEventAdmin,
    MovementAdmin,
    WriteOffReportAdmin,
    ReplacementSuggestionAdmin,
)
from src.adminpanel.auth import authentication_backend
from src.database import engine
from src.tasks.warranty_suggestions import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_part_types)
app.include_router(router_device_types)
app.include_router(router_locations)
app.include_router(router_devices)
app.include_router(router_movements)
app.include_router(router_movements_admin)
app.include_router(router_inventory_events)
app.include_router(router_inventory_items)
app.include_router(router_maintenance)
app.include_router(router_failure)
app.include_router(router_replacement_suggestions)
app.include_router(router_reports)
app.include_router(router_analytics)
app.include_router(router_stats)

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(DeviceAdmin)
admin.add_view(DeviceTypeAdmin)
admin.add_view(LocationAdmin)
admin.add_view(PartTypeAdmin)
admin.add_view(FailureRecordAdmin)
admin.add_view(MaintenanceTaskAdmin)
admin.add_view(InventoryItemAdmin)
admin.add_view(InventoryEventAdmin)
admin.add_view(MovementAdmin)
admin.add_view(WriteOffReportAdmin)
admin.add_view(ReplacementSuggestionAdmin)

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

datacenter_load_gauge = Gauge("datacenter_load", "Current datacenter load", ["hour"])
backend_action_counter = Counter(
    "backend_action_total", "Total backend actions", ["action"]
)


class ActionCounterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        action = f"{request.method}_{request.url.path}"
        backend_action_counter.labels(action=action).inc()
        response = await call_next(request)
        return response


app.add_middleware(ActionCounterMiddleware)

Instrumentator().instrument(app).expose(app)
