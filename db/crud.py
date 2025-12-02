from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import SlugAlreadyExistsError
from .models import ShortURL


async def add_slug_to_database(slug: str, long_url: str, session: AsyncSession):
    new_slug = ShortURL(slug=slug, long_url=long_url)
    session.add(new_slug)
    try:
        await session.commit()
    except IntegrityError:
        raise SlugAlreadyExistsError


async def find_long_url_from_database(slug: str, session: AsyncSession) -> str | None:
    query = await session.execute(select(ShortURL).where(ShortURL.slug == slug))
    res = query.scalar_one_or_none()
    return res.long_url if res.long_url else None
