from service import generate_short_url, get_url_by_slug
from sqlalchemy import select
from db import ShortURL


async def test_generate_short_url(session):
    slug = await generate_short_url(long_url="https://www.google.com/", session=session)

    query = await session.execute(select(ShortURL).where(ShortURL.slug == slug))
    res = query.scalar_one_or_none()

    assert res is not None

    assert len(slug) == 6


async def test_get_url_by_slug(session):
    slug = await generate_short_url(long_url="https://www.google.com/", session=session)

    long_url = await get_url_by_slug(slug=slug, session=session)

    query = await session.execute(select(ShortURL).where(ShortURL.slug == slug))
    res = query.scalar_one_or_none()

    assert res is not None and res.long_url == long_url
