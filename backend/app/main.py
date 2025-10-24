from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS, DEBUG
from app.database import close_database, ensure_indexes, get_collection, initialize_database, mongodb_enabled
from app.models import CartItem, Order, OrderCreate, Product, ProductCreate, User, UserCreate, UserLogin
from app.seed_data import PRODUCTS, USERS
from app.security import create_access_token, hash_password, verify_password

app = FastAPI(title="CAPZONE API", version="1.0.0", description="Backend service for the CAPZONE storefront")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCT_STORE: List[Dict[str, Any]] = [dict(item) for item in PRODUCTS]
USER_STORE: List[Dict[str, Any]] = [dict(user) for user in USERS]
ORDER_STORE: List[Dict[str, Any]] = []


@app.on_event("startup")
async def startup_event():
    await initialize_database()
    await ensure_indexes()

    products_collection = get_collection("products")
    if products_collection is not None:
        product_count = await products_collection.count_documents({})
        if product_count == 0:
            await products_collection.insert_many(PRODUCT_STORE)

    users_collection = get_collection("users")
    if users_collection is not None:
        user_count = await users_collection.count_documents({})
        if user_count == 0:
            seeded_users = [dict(user) for user in USERS]
            for user in seeded_users:
                user["password_hash"] = hash_password(user["password"])
                user.pop("password", None)
            await users_collection.insert_many(seeded_users)

    for user in USER_STORE:
        if "password_hash" not in user:
            user["password_hash"] = hash_password(user["password"])
            user.pop("password", None)


@app.on_event("shutdown")
async def shutdown_event():
    await close_database()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "debug": DEBUG, "service": "capzone-api", "mongodb_connected": mongodb_enabled()}


async def read_products_from_store():
    products_collection = get_collection("products")
    if products_collection is not None:
        docs = await products_collection.find({}).to_list(length=None)
        return [dict(doc) for doc in docs]
    return PRODUCT_STORE


async def read_users_from_store():
    users_collection = get_collection("users")
    if users_collection is not None:
        docs = await users_collection.find({}).to_list(length=None)
        return [dict(doc) for doc in docs]
    return USER_STORE


async def read_orders_from_store():
    orders_collection = get_collection("orders")
    if orders_collection is not None:
        docs = await orders_collection.find({}).to_list(length=None)
        return [dict(doc) for doc in docs]
    return ORDER_STORE


@app.get("/api/products", response_model=List[Product])
async def list_products():
    return await read_products_from_store()


@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    products = await read_products_from_store()
    product = next((item for item in products if item["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    slug = payload.name.lower().replace(" ", "-")
    product = {
        "id": f"p-{len(PRODUCT_STORE) + 101}",
        "slug": slug,
        **payload.model_dump(),
    }
    products_collection = get_collection("products")
    if products_collection is not None:
        await products_collection.insert_one(product)
    else:
        PRODUCT_STORE.append(product)
    return product


@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate):
    users_collection = get_collection("users")
    existing_users = await read_users_from_store()
    if any(user.get("email", "").lower() == payload.email.lower() for user in existing_users):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "id": f"u-{len(USER_STORE) + 1:03d}",
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "is_admin": payload.is_admin,
    }
    if users_collection is not None:
        await users_collection.insert_one(user)
    else:
        USER_STORE.append(user)
    return {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "is_admin": user["is_admin"]}


@app.post("/api/auth/login")
async def login_user(payload: UserLogin):
    users = await read_users_from_store()
    user = next((item for item in users if item.get("email", "").lower() == payload.email.lower()), None)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_access_token(user["id"]), "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "is_admin": user["is_admin"]}}


@app.get("/api/admin/summary")
async def admin_summary():
    orders = await read_orders_from_store()
    return {
        "total_products": len(await read_products_from_store()),
        "available_products": sum(1 for item in await read_products_from_store() if item["in_stock"]),
        "total_orders": len(orders),
        "revenue": round(sum(order["total"] for order in orders), 2),
    }


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate):
    products = await read_products_from_store()
    total = sum(item.quantity * next(product["price"] for product in products if product["id"] == item.product_id) for item in payload.items)
    order = {
        "id": f"o-{len(ORDER_STORE) + 1:03d}",
        "user_id": "guest-user",
        "items": [item.model_dump() for item in payload.items],
        "total": round(total, 2),
        "shipping_address": payload.shipping_address,
        "contact_phone": payload.contact_phone,
        "status": "pending",
    }
    orders_collection = get_collection("orders")
    if orders_collection is not None:
        await orders_collection.insert_one(order)
    else:
        ORDER_STORE.append(order)
    return order


@app.get("/api/orders")
async def list_orders():
    return await read_orders_from_store()
