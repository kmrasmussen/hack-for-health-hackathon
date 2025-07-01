import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# This code is no longer necessary because the .env file is correct.
# if DATABASE_URL.startswith("postgresql://"):
#     DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Setup the async database engine
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Define the Transcript table model
class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="processing")
    whisper_transcript: Mapped[str | None] = mapped_column(String)
    corti_transcript: Mapped[str | None] = mapped_column(String)
    improved_transcript: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

async def init_db():
    """Creates the database tables."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use this to reset the DB
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get a DB session in API endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session