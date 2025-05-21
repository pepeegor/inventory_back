from fastapi import FastAPI
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


app = FastAPI()

app.include_router(router_auth)
app.include_router(router_part_types)
app.include_router(router_device_types)
app.include_router(router_locations)
app.include_router(router_devices)
app.include_router(router_movements)
app.include_router(router_inventory_events)
app.include_router(router_inventory_items)
app.include_router(router_maintenance)
app.include_router(router_failure)
