import asyncio
import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.database import engine
from app.models.rbac import Role, Permission

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_database() -> None:
    """
    Base seeding system.
    Runs prior to application start to ensure required base data exists.
    """
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        # Define roles
        roles = ["Admin", "Premium User", "Standard User"]
        for role_name in roles:
            result = await db.execute(select(Role).where(Role.name == role_name))
            if not result.scalars().first():
                logger.info(f"Seeding Role: {role_name}")
                db.add(Role(name=role_name, description=f"{role_name} role"))
        
        await db.commit()
    
    logger.info("Database seeding completed.")

if __name__ == "__main__":
    asyncio.run(seed_database())
