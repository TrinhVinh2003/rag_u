from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

# Tạo engine
engine = create_async_engine(str(settings.db_url), echo=True)

# Tạo session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency: Lấy phiên làm việc
async def get_db_session() -> AsyncSession:  # noqa: D103
    async with SessionLocal() as session:
        yield session
