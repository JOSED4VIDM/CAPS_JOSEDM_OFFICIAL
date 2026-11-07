from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import ADMIN_EMAIL, ALLOWED_ORIGINS, DEBUG
from app.database import close_database, ensure_indexes, get_collection, initialize_database, mongodb_enabled
from app.models import Order, OrderCreate, Product, ProductCreate, User, UserCreate, UserLogin
from app.seed_data import PRODUCTS, USERS
from app.security import create_access_token, get_current_user, hash_password, verify_password

app = FastAPI(title="CAPZONE API", version="1.0.0", description="Servicio de API para la tienda CAPZONE.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).resolve().parent / "local_store.json"


def persist_local_store() -> None:
    payload = {
        "products": PRODUCT_STORE,
        "users": USER_STORE,
        "orders": ORDER_STORE,
    }

    def json_default(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2, default=json_default)


def load_local_store() -> None:
    global PRODUCT_STORE, USER_STORE, ORDER_STORE
    if not DATA_FILE.exists():
        PRODUCT_STORE = [dict(item) for item in PRODUCTS]
        USER_STORE = [dict(user) for user in USERS]
        ORDER_STORE = []
        persist_local_store()
        return

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        PRODUCT_STORE = payload.get("products", [dict(item) for item in PRODUCTS])
        USER_STORE = payload.get("users", [dict(user) for user in USERS])
        ORDER_STORE = payload.get("orders", [])
    except (json.JSONDecodeError, OSError):
        PRODUCT_STORE = [dict(item) for item in PRODUCTS]
        USER_STORE = [dict(user) for user in USERS]
        ORDER_STORE = []
        persist_local_store()


load_local_store()


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
        if user_count == 0 and USERS:
            seeded_users = [dict(user) for user in USERS]
            for user in seeded_users:
                user["password_hash"] = hash_password(user["password"])
                user.pop("password", None)
            await users_collection.insert_many(seeded_users)

    for user in USER_STORE:
        if "password_hash" not in user:
            user["password_hash"] = hash_password(user["password"])
            user.pop("password", None)

    if users_collection is not None and ADMIN_EMAIL and ADMIN_EMAIL != "admin@capzone.com":
        await users_collection.update_one(
            {"email": "admin@capzone.com"},
            {"$set": {"is_admin": False}},
        )
    elif ADMIN_EMAIL and ADMIN_EMAIL != "admin@capzone.com":
        for user in USER_STORE:
            if user.get("email", "").lower() == "admin@capzone.com":
                user["is_admin"] = False

    if not mongodb_enabled():
        persist_local_store()


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


async def get_user_by_id(user_id: str):
    users = await read_users_from_store()
    return next((user for user in users if user.get("id") == user_id), None)


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    user = await get_user_by_id(current_user["id"])
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta sección.")
    return user


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
        raise HTTPException(status_code=404, detail="No encontramos ese producto.")
    return product


@app.post("/api/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, _current_user: Dict[str, Any] = Depends(require_admin)):
    slug = payload.name.lower().replace(" ", "-")
    product = {
        "id": f"p-{uuid4().hex[:12]}",
        "slug": slug,
        **payload.model_dump(),
    }
    products_collection = get_collection("products")
    if products_collection is not None:
        await products_collection.insert_one(product)
    else:
        PRODUCT_STORE.append(product)
        persist_local_store()
    return product


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, _current_user: Dict[str, Any] = Depends(require_admin)):
    products_collection = get_collection("products")
    if products_collection is not None:
        result = await products_collection.delete_one({"id": product_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="El producto no existe.")
    else:
        existing = next((item for item in PRODUCT_STORE if item["id"] == product_id), None)
        if existing is None:
            raise HTTPException(status_code=404, detail="El producto no existe.")
        PRODUCT_STORE[:] = [item for item in PRODUCT_STORE if item["id"] != product_id]
        persist_local_store()
    return {"success": True, "product_id": product_id}


@app.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate):
    users_collection = get_collection("users")
    existing_users = await read_users_from_store()
    if any(user.get("email", "").lower() == payload.email.lower() for user in existing_users):
        raise HTTPException(status_code=400, detail="Este correo ya tiene una cuenta registrada.")
    if ADMIN_EMAIL and payload.email.lower() == ADMIN_EMAIL:
        raise HTTPException(
            status_code=403,
            detail="La cuenta de administración debe estar configurada previamente.",
        )
    user = {
        "id": f"u-{uuid4().hex[:12]}",
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "is_admin": False,
    }
    if users_collection is not None:
        await users_collection.insert_one(user)
    else:
        USER_STORE.append(user)
        persist_local_store()
    return {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "is_admin": user["is_admin"]}


@app.post("/api/auth/login")
async def login_user(payload: UserLogin):
    users = await read_users_from_store()
    user = next((item for item in users if item.get("email", "").lower() == payload.email.lower()), None)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="El correo o la contraseña no son correctos.")
    is_admin = bool(user.get("is_admin"))
    return {"token": create_access_token(user["id"]), "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "is_admin": is_admin}}


@app.get("/api/admin/summary")
async def admin_summary(_current_user: Dict[str, Any] = Depends(require_admin)):
    orders = await read_orders_from_store()
    return {
        "total_products": len(await read_products_from_store()),
        "available_products": sum(1 for item in await read_products_from_store() if item["in_stock"]),
        "total_orders": len(orders),
        "revenue": round(sum(order["total"] for order in orders), 2),
    }


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    products = await read_products_from_store()
    products_by_id = {product["id"]: product for product in products}
    missing_product = next((item.product_id for item in payload.items if item.product_id not in products_by_id), None)
    if missing_product:
        raise HTTPException(status_code=404, detail="Uno de los productos del pedido ya no está disponible.")
    customer = await get_user_by_id(current_user["id"])
    if not customer:
        raise HTTPException(status_code=401, detail="Inicia sesión de nuevo para continuar.")
    total = sum(item.quantity * products_by_id[item.product_id]["price"] for item in payload.items)
    order = {
        "id": f"o-{uuid4().hex[:12]}",
        "user_id": current_user["id"],
        "customer_name": customer.get("full_name", ""),
        "customer_email": customer.get("email", ""),
        "created_at": datetime.now(timezone.utc),
        "items": [item.model_dump() for item in payload.items],
        "total": round(total, 2),
        "shipping_address": payload.shipping_address,
        "contact_phone": payload.contact_phone,
        "status": "pendiente",
    }
    orders_collection = get_collection("orders")
    if orders_collection is not None:
        await orders_collection.insert_one(order)
    else:
        ORDER_STORE.append(order)
        persist_local_store()
    return order


@app.get("/api/orders/me", response_model=List[Order])
async def list_my_orders(current_user: Dict[str, Any] = Depends(get_current_user)):
    orders = await read_orders_from_store()
    return [order for order in orders if order.get("user_id") == current_user["id"]]


@app.get("/api/orders", response_model=List[Order])
async def list_orders(_current_user: Dict[str, Any] = Depends(require_admin)):
    return await read_orders_from_store()
