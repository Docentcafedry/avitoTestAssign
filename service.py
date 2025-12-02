from sqlalchemy.ext.asyncio import AsyncSession
from utils import generate_random_slug
from db import add_slug_to_database, find_long_url_from_database
from exceptions import SlugAlreadyExistsError, NoLongUrlFoundError, URLValidationError
from utils import validate_url


async def generate_short_url(long_url: str, session: AsyncSession):
    if not validate_url(long_url):
        raise URLValidationError

    async def _generate_slug_and_add_to_db() -> str:
        slug = generate_random_slug()
        await add_slug_to_database(slug=slug, long_url=long_url, session=session)
        return slug

    for attempt in range(5):
        try:
            slug = await _generate_slug_and_add_to_db()
            return slug
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex


async def generate_short_url_with_custom_slug(
    long_url: str, slug: str, session: AsyncSession
):
    if not validate_url(long_url):
        raise URLValidationError

    async def _generate_slug_and_add_to_db():
        await add_slug_to_database(slug=slug, long_url=long_url, session=session)

    for attempt in range(5):
        try:
            await _generate_slug_and_add_to_db()
            return slug
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex


async def get_url_by_slug(slug: str, session: AsyncSession) -> str:
    long_url = await find_long_url_from_database(slug=slug, session=session)
    if not long_url:
        raise NoLongUrlFoundError
    return long_url
