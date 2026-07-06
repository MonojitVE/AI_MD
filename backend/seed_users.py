import asyncio
from app.database import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    async with AsyncSession(async_engine) as session:
        # Create Admin
        admin = User(
            employee_id="ADMIN001",
            first_name="System",
            last_name="Admin",
            email="admin@sentryfab.com",
            password_hash=pwd_context.hash("admin123"),
            role="admin",
            department="IT"
        )
        # Create Employee
        emp = User(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@sentryfab.com",
            password_hash=pwd_context.hash("emp123"),
            role="employee",
            department="Maintenance"
        )
        session.add(admin)
        session.add(emp)
        await session.commit()
        print("Users seeded!")

asyncio.run(seed())
