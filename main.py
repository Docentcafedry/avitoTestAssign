from contextlib import asynccontextmanager
from db import engine, Base
from fastapi import FastAPI, Body, HTTPException, status
from typing import Annotated
from depends import db_connection
from service import (
    generate_short_url,
    get_url_by_slug,
    generate_short_url_with_custom_slug,
)
from exceptions import SlugAlreadyExistsError, NoLongUrlFoundError, URLValidationError
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/short_url", status_code=status.HTTP_201_CREATED)
async def generate_slug(
    long_url: Annotated[str, Body(embed=True)], session: db_connection
):
    try:
        new_slug = await generate_short_url(long_url=long_url, session=session)
    except (SlugAlreadyExistsError, URLValidationError) as e:
        if isinstance(e, SlugAlreadyExistsError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error during slug generation",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Validation URL error",
            )

    return {"data": new_slug}


@app.post("/custom/short_url", status_code=status.HTTP_201_CREATED)
async def generate_custom_slug(
    long_url: Annotated[str, Body(embed=True)],
    slug: Annotated[str, Body(embed=True, max_length=10)],
    session: db_connection,
):
    try:
        await generate_short_url_with_custom_slug(
            long_url=long_url, slug=slug, session=session
        )
    except (SlugAlreadyExistsError, URLValidationError) as e:
        if isinstance(e, SlugAlreadyExistsError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error during slug generation",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Validation URL error",
            )

    return {"data": slug}


@app.get("/{slug}", status_code=status.HTTP_302_FOUND)
async def redirect_to_full_link(slug: str, session: db_connection):
    try:
        long_url = await get_url_by_slug(slug=slug, session=session)
        return RedirectResponse(url=long_url, status_code=302)
    except NoLongUrlFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Slug was not found"
        )
