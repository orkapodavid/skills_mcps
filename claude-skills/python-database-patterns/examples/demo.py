import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

# --- 1. Define Models ---
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

# --- 2. Setup Database ---
# Using SQLite for this demo so no external server is required.
# In production/Docker, use: "postgresql+asyncpg://user:pass@localhost/db"
DATABASE_URL = "sqlite+aiosqlite:///./demo.db"

async def main():
    print(f"Connecting to {DATABASE_URL}...")

    # Create Async Engine
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Create Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Clean slate
        await conn.run_sync(Base.metadata.create_all)

    # Create Session Factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # --- 3. Insert Data ---
    print("\n--- Inserting User ---")
    async with async_session() as session:
        new_user = User(name="Alice", email="alice@example.com")
        session.add(new_user)
        await session.commit()
        print(f"Created user: {new_user.name}")

    # --- 4. Query Data ---
    print("\n--- Querying User ---")
    async with async_session() as session:
        stmt = select(User).where(User.name == "Alice")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            print(f"Found user: {user.name} ({user.email})")
        else:
            print("User not found")

    await engine.dispose()

if __name__ == "__main__":
    # Check for dependencies
    try:
        import aiosqlite
    except ImportError:
        print("Error: Missing dependency 'aiosqlite'. Run: pip install aiosqlite sqlalchemy")
        exit(1)

    asyncio.run(main())
