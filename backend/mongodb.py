from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from backend.config import get_optional_env


@asynccontextmanager
async def mongo_lifespan(app: FastAPI) -> AsyncIterator[None]:
    uri = get_optional_env("MONGODB_URI")
    database_name = get_optional_env("MONGODB_DB", "arkham_social")

    app.state.mongo_client = None
    app.state.mongo_db = None

    if uri:
        client = AsyncMongoClient(uri, serverSelectionTimeoutMS=3000)
        app.state.mongo_client = client
        app.state.mongo_db = client[database_name]
        try:
            await client.admin.command("ping")
            await create_indexes(app.state.mongo_db)
        except PyMongoError:
            await client.close()
            app.state.mongo_client = None
            app.state.mongo_db = None

    try:
        yield
    finally:
        if app.state.mongo_client is not None:
            await app.state.mongo_client.close()


async def create_indexes(database) -> None:
    await database.posts.create_index([("created_at", -1)])
    await database.posts.create_index([("author_id", 1), ("created_at", -1)])
    await database.comments.create_index([("post_id", 1), ("created_at", 1)])
    await database.reactions.create_index(
        [("post_id", 1), ("user_id", 1)],
        unique=True,
    )
    await database.follows.create_index(
        [("follower_id", 1), ("followed_id", 1)],
        unique=True,
    )
