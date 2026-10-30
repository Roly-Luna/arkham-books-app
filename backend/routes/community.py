from datetime import datetime, timezone
from typing import Literal

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError, PyMongoError

from backend.database import get_connection

router = APIRouter(prefix="/community", tags=["community"])


class PostInput(BaseModel):
    author_id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=2000)
    kind: Literal["post", "review", "recommendation"] = "post"
    book_title: str | None = Field(default=None, max_length=200)


class CommentInput(BaseModel):
    author_id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=1000)


class ReactionInput(BaseModel):
    user_id: int = Field(gt=0)
    reaction: Literal["like", "love", "insightful"] = "like"


class FollowInput(BaseModel):
    follower_id: int = Field(gt=0)
    followed_id: int = Field(gt=0)


def get_mongo(request: Request):
    database = getattr(request.app.state, "mongo_db", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Community database is not configured or unavailable",
        )
    return database


def ensure_user_exists(user_id: int) -> None:
    query = "SELECT id_usuario FROM usuario WHERE id_usuario = %s;"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                if cursor.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="User validation failed") from error


def serialize(document: dict) -> dict:
    document["id"] = str(document.pop("_id"))
    for field in ("created_at", "updated_at"):
        if field in document and isinstance(document[field], datetime):
            document[field] = document[field].isoformat()
    return document


@router.get("/health")
async def community_health(request: Request):
    database = get_mongo(request)
    try:
        await database.command("ping")
        return {"status": "ok", "database": "mongodb"}
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="MongoDB unavailable") from error


@router.get("/feed")
async def get_feed(
    request: Request,
    limit: int = Query(default=20, ge=1, le=50),
    skip: int = Query(default=0, ge=0),
):
    database = get_mongo(request)
    try:
        cursor = database.posts.find().sort("created_at", -1).skip(skip).limit(limit)
        posts = [serialize(post) async for post in cursor]
        return {"items": posts, "limit": limit, "skip": skip}
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="Could not load feed") from error


@router.post("/posts", status_code=201)
async def create_post(payload: PostInput, request: Request):
    ensure_user_exists(payload.author_id)
    database = get_mongo(request)
    document = {
        "author_id": payload.author_id,
        "content": payload.content.strip(),
        "kind": payload.kind,
        "book_title": payload.book_title,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }
    try:
        result = await database.posts.insert_one(document)
        document["_id"] = result.inserted_id
        return serialize(document)
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="Could not create post") from error


@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: str, request: Request):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    database = get_mongo(request)
    cursor = database.comments.find({"post_id": ObjectId(post_id)}).sort("created_at", 1)
    return [serialize(comment) async for comment in cursor]


@router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: str, payload: CommentInput, request: Request):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    ensure_user_exists(payload.author_id)
    database = get_mongo(request)
    if await database.posts.find_one({"_id": ObjectId(post_id)}) is None:
        raise HTTPException(status_code=404, detail="Post not found")
    document = {
        "post_id": ObjectId(post_id),
        "author_id": payload.author_id,
        "content": payload.content.strip(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await database.comments.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize(document)


@router.put("/posts/{post_id}/reaction")
async def set_reaction(post_id: str, payload: ReactionInput, request: Request):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    ensure_user_exists(payload.user_id)
    database = get_mongo(request)
    if await database.posts.find_one({"_id": ObjectId(post_id)}) is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await database.reactions.update_one(
        {"post_id": ObjectId(post_id), "user_id": payload.user_id},
        {"$set": {"reaction": payload.reaction, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"status": "ok", "reaction": payload.reaction}


@router.delete("/posts/{post_id}/reaction/{user_id}")
async def remove_reaction(post_id: str, user_id: int, request: Request):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    database = get_mongo(request)
    result = await database.reactions.delete_one(
        {"post_id": ObjectId(post_id), "user_id": user_id}
    )
    return {"deleted": result.deleted_count == 1}


@router.post("/follow", status_code=201)
async def follow_user(payload: FollowInput, request: Request):
    if payload.follower_id == payload.followed_id:
        raise HTTPException(status_code=400, detail="A user cannot follow themselves")
    ensure_user_exists(payload.follower_id)
    ensure_user_exists(payload.followed_id)
    database = get_mongo(request)
    try:
        await database.follows.insert_one({
            "follower_id": payload.follower_id,
            "followed_id": payload.followed_id,
            "created_at": datetime.now(timezone.utc),
        })
        return {"status": "following"}
    except DuplicateKeyError:
        return {"status": "already_following"}
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="Could not follow user") from error
