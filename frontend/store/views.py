import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

API_URL = getattr(settings, "BASE_URL", "http://localhost:8000")


def get_products():
    try:
        response = requests.get(f"{API_URL}/api/products", timeout=10)
        if response.ok:
            return response.json()
    except requests.RequestException:
        pass
    return [
        {
            "id": "p-101",
            "name": "Urban Black Snapback",
            "slug": "urban-black-snapback",
            "category": "Snapback",
            "price": 39.99,
            "original_price": 49.99,
            "rating": 4.8,
            "reviews": 128,
            "image_url": "https://images.unsplash.com/photo-1521369909026-2afc9123a8c7?auto=format&fit=crop&w=1200&q=80",
            "in_stock": True,
            "description": "A premium urban snapback designed for everyday streetwear styling.",
            "features": ["Structured fit", "Adjustable closure", "High-quality woven fabric"],
            "tags": ["best seller", "streetwear"],
        }
    ]


def cart_summary(request):
    cart = request.session.get("cart", {})
    total_items = sum(item.get("quantity", 0) for item in cart.values())
    return total_items


def catalog(request: HttpRequest):
    products = get_products()
    return render(request, "catalog.html", {"products": products, "cart_count": cart_summary(request)})


def product_detail(request: HttpRequest, slug: str):
    products = get_products()
    product = next((item for item in products if item["slug"] == slug), None)
    if not product:
        return HttpResponse("Product not found", status=404)
    return render(request, "product_detail.html", {"product": product, "cart_count": cart_summary(request)})


def add_to_cart(request: HttpRequest, product_id: str):
    cart = request.session.get("cart", {})
    current = cart.get(product_id, {"quantity": 0})
    current["quantity"] = current.get("quantity", 0) + 1
    cart[product_id] = current
    request.session["cart"] = cart
    messages.success(request, "Producto agregado al carrito")
    return redirect("catalog")


def remove_from_cart(request: HttpRequest, product_id: str):
    cart = request.session.get("cart", {})
    cart.pop(product_id, None)
    request.session["cart"] = cart
    messages.info(request, "Producto eliminado del carrito")
    return redirect("cart")


def cart(request: HttpRequest):
    cart = request.session.get("cart", {})
    products = get_products()
    cart_items = []
    for product_id, details in cart.items():
        product = next((item for item in products if item["id"] == product_id), None)
        if product:
            cart_items.append({"product": product, "quantity": details.get("quantity", 1)})
    subtotal = sum(item["product"]["price"] * item["quantity"] for item in cart_items)
    return render(request, "cart.html", {"cart_items": cart_items, "subtotal": subtotal, "cart_count": cart_summary(request)})


def checkout(request: HttpRequest):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        if not cart:
            messages.error(request, "Tu carrito está vacío")
            return redirect("catalog")
        order_payload = {
            "items": [{"product_id": product_id, "quantity": details.get("quantity", 1)} for product_id, details in cart.items()],
            "shipping_address": request.POST.get("shipping_address", "Main street 123"),
            "contact_phone": request.POST.get("contact_phone", "+57 300 000 0000"),
        }
        try:
            response = requests.post(f"{API_URL}/api/orders", json=order_payload, timeout=10)
            if response.ok:
                request.session["cart"] = {}
                messages.success(request, "Pedido creado con éxito")
                return redirect("catalog")
        except requests.RequestException:
            pass
        messages.error(request, "No se pudo completar la compra. Intenta de nuevo.")
        return redirect("cart")
    return render(request, "checkout.html", {"cart_count": cart_summary(request)})


def login_view(request: HttpRequest):
    if request.method == "POST":
        payload = {"email": request.POST.get("email"), "password": request.POST.get("password")}
        try:
            response = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
            data = response.json()
            if response.ok:
                request.session["token"] = data["token"]
                request.session["user"] = data["user"]
                messages.success(request, "Inicio de sesión correcto")
                return redirect("catalog")
            messages.error(request, data.get("detail", "Credenciales inválidas"))
        except requests.RequestException:
            messages.error(request, "No fue posible iniciar sesión")
    return render(request, "login.html", {"cart_count": cart_summary(request)})


def register_view(request: HttpRequest):
    if request.method == "POST":
        payload = {
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
        }
        try:
            response = requests.post(f"{API_URL}/api/auth/register", json=payload, timeout=10)
            data = response.json()
            if response.ok:
                messages.success(request, "Cuenta creada con éxito")
                return redirect("login")
            messages.error(request, data.get("detail", "No se pudo crear la cuenta"))
        except requests.RequestException:
            messages.error(request, "No fue posible registrar la cuenta")
    return render(request, "register.html", {"cart_count": cart_summary(request)})


def logout_view(request: HttpRequest):
    request.session.flush()
    messages.info(request, "Sesión cerrada")
    return redirect("catalog")


def admin_dashboard(request: HttpRequest):
    try:
        response = requests.get(f"{API_URL}/api/admin/summary", timeout=10)
        stats = response.json() if response.ok else {"total_products": 0, "available_products": 0, "total_orders": 0, "revenue": 0}
    except requests.RequestException:
        stats = {"total_products": 0, "available_products": 0, "total_orders": 0, "revenue": 0}
    return render(request, "admin_dashboard.html", {"stats": stats, "cart_count": cart_summary(request)})
