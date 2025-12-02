from .conftest import client
from sqlalchemy import select
from db import ShortURL


async def test_generate_short_url(session):
    generate_slug_response = client.post(
        "/short_url",
        json={"long_url": "https://www.google.com/"},
    )
    response_slug = generate_slug_response.json()["data"]
    assert generate_slug_response.status_code == 201
    query = await session.execute(
        select(ShortURL).where(ShortURL.slug == response_slug)
    )
    res = query.scalar_one_or_none()

    assert res is not None and res.slug == response_slug


async def test_generate_short_url_invalid_long_url(session):
    generate_slug_response = client.post(
        "/short_url",
        json={"long_url": "dsadsadsa"},
    )
    assert generate_slug_response.status_code == 400
