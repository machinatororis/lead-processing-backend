import asyncio

from sqlalchemy import select

from core.app.db.models import Affiliate, Offer
from core.app.db.session import async_session_factory


async def seed() -> None:
    async with async_session_factory() as session:
        existing_affiliates = await session.execute(select(Affiliate))
        existing_offers = await session.execute(select(Offer))

        if existing_affiliates.scalars().first() or existing_offers.scalars().first():
            print("Seed data already exists. Skipping.")
            return

        affiliates = [
            Affiliate(id=1, name="Test Affiliate"),
            Affiliate(id=2, name="Second Affiliate"),
        ]

        offers = [
            Offer(id=1, name="Test Offer"),
            Offer(id=2, name="Second Offer"),
        ]

        session.add_all([*affiliates, *offers])
        await session.commit()

        print("Seed data created.")
        print("Affiliates: 1, 2")
        print("Offers: 1, 2")


if __name__ == "__main__":
    asyncio.run(seed())