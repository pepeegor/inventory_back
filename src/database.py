from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine = create_async_engine(
    settings.db_url,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

def _register_models():
    import src.users.models
    import src.locations.models
    import src.device_types.models
    import src.part_types.models
    import src.devices.models
    import src.movements.models
    import src.inventory_events.models
    import src.inventory_items.models
    import src.maintenance_tasks.models
    import src.write_off_reports.models
    import src.failure_records.models
    import src.replacement_suggestions.models
    

_register_models()
