from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    original_price: Optional[float] = None
    rating: float = 0.0
    reviews: int = 0
    image_url: str
    in_stock: bool = True
    description: str
    features: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: str
    slug: str


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    full_name: str
    email: str
    is_admin: bool = False


class CartItemInput(BaseModel):
    product_id: str
    quantity: int = 1


class CartItem(BaseModel):
    product_id: str
    quantity: int


class OrderCreate(BaseModel):
    items: List[CartItem]
    shipping_address: str
    contact_phone: str


class Order(BaseModel):
    id: str
    user_id: str
    items: List[CartItem]
    total: float
    shipping_address: str
    contact_phone: str
    status: str = "pending"
