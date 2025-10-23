from __future__ import annotations

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import DEBUG, MONGODB_URL

logger = logging.getLogger(__name__)
client: AsyncIOMotorClient | None = None
db: Any = None


def mongodb_enabled() -> bool:
    return db is not None and client is not None


async def initialize_database() -> None:
    global client, db

    if not MONGODB_URL:
        if not DEBUG:
            raise RuntimeError("MONGODB_URL must be configured when DEBUG is false.")
        logger.info("MONGODB_URL is not configured; using in-memory data storage.")
        client = None
        db = None
        return

    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        db = client["techgear"]
        await db.command("ping")
        logger.info("Connected to MongoDB Atlas successfully.")
    except Exception as exc:  # pragma: no cover - runtime dependency on external service
        logger.warning("Could not connect to MongoDB: %s. Falling back to in-memory storage.", exc)
        if client is not None:
            client.close()
        client = None
        db = None
        if not DEBUG:
            raise RuntimeError("Could not connect to MongoDB while running with DEBUG=false.") from exc


def get_collection(name: str):
    return db[name] if mongodb_enabled() else None


async def ensure_indexes():
    if not mongodb_enabled():
        return
    products = db["products"]
    await products.create_index("slug", unique=True)
    await products.create_index("category")
    users = db["users"]
    await users.create_index("email", unique=True)
    orders = db["orders"]
    await orders.create_index("user_id")


async def close_database() -> None:
    global client, db
    if client is not None:
        client.close()
    client = None
    db = None
