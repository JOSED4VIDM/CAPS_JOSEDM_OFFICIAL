import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

API_URL = getattr(settings, "BASE_URL", "http://localhost:8000")
LOCAL_PRODUCT_CONTENT = {
    "p-101": {
        "image": "cap-nyc.jpg",
        "name": "Gorra New York Negra",
        "category": "Béisbol",
        "description": "Gorra negra de perfil estructurado, inspirada en el clásico estilo de Nueva York.",
        "features": ["Perfil estructurado", "Cierre ajustable", "Visera plana"],
        "slug": "urban-black-snapback",
        "price": 39.99,
        "original_price": 49.99,
        "rating": 4.8,
        "reviews": 128,
        "in_stock": True,
    },
    "p-102": {
        "image": "cap-bulls.jpg",
        "name": "Gorra Bulls Roja",
        "category": "Baloncesto",
        "description": "Diseño rojo de alto contraste para sumar carácter a cualquier combinación urbana.",
        "features": ["Color rojo intenso", "Cierre ajustable", "Diseño urbano"],
        "slug": "fresh-run-cap",
        "price": 34.99,
        "original_price": 44.99,
        "rating": 4.7,
        "reviews": 94,
        "in_stock": True,
    },
    "p-103": {
        "image": "cap-la.jpg",
        "name": "Gorra Los Angeles Beige",
        "category": "Béisbol",
        "description": "Tono beige versátil con un perfil limpio para usar todos los días.",
        "features": ["Tono beige", "Perfil estructurado", "Cierre ajustable"],
        "slug": "monarch-flex-cap",
        "price": 52.99,
        "original_price": 64.99,
        "rating": 4.9,
        "reviews": 211,
        "in_stock": True,
    },
    "p-104": {
        "image": "cap-raiders.jpg",
        "name": "Gorra Raiders Negra",
        "category": "Fútbol americano",
        "description": "Una silueta negra clásica con detalles gráficos para un estilo decidido.",
        "features": ["Diseño negro", "Cierre ajustable", "Visera plana"],
        "slug": "night-shift-beanie",
        "price": 29.99,
        "original_price": 39.99,
        "rating": 4.6,
        "reviews": 73,
        "in_stock": False,
    },
    "p-105": {
        "image": "cap-sox.jpg",
        "name": "Gorra Chicago a Rayas",
        "category": "Béisbol",
        "description": "Gorra negra a rayas con visera blanca, una mezcla deportiva y atemporal.",
        "features": ["Patrón a rayas", "Visera blanca", "Cierre ajustable"],
        "slug": "the-street-pro",
        "price": 46.99,
        "original_price": 58.99,
        "rating": 4.8,
        "reviews": 186,
        "in_stock": True,
    },
    "p-106": {
        "image": "cap-miami.jpg",
        "name": "Gorra Miami Negra y Roja",
        "category": "Baloncesto",
        "description": "Base negra con detalles rojos para un contraste distintivo y actual.",
        "features": ["Detalles rojos", "Perfil estructurado", "Cierre ajustable"],
        "slug": "crest-vintage-cap",
        "price": 41.49,
        "original_price": 52.99,
        "rating": 4.7,
        "reviews": 142,
        "in_stock": True,
    },
}


def localize_products(products):
    for product in products:
        content = LOCAL_PRODUCT_CONTENT.get(product.get("id"))
        if content:
            product["image_url"] = f"/static/images/{content['image']}"
            product["name"] = content["name"]
            product["category"] = content["category"]
            product["description"] = content["description"]
            product["features"] = content["features"]
    return products


def get_products():
    try:
        response = requests.get(f"{API_URL}/api/products", timeout=10)
        if response.ok:
            return localize_products(response.json())
    except requests.RequestException:
        pass
    fallback_products = [
        {
            "id": product_id,
            "name": content["name"],
            "slug": content["slug"],
            "category": content["category"],
            "price": content["price"],
            "original_price": content["original_price"],
            "rating": content["rating"],
            "reviews": content["reviews"],
            "image_url": f"/static/images/{content['image']}",
            "in_stock": content["in_stock"],
            "description": content["description"],
            "features": content["features"],
            "tags": ["colección CAPZONE"],
        }
        for product_id, content in LOCAL_PRODUCT_CONTENT.items()
    ]
    return localize_products(fallback_products)


def cart_summary(request):
    cart = request.session.get("cart", {})
    total_items = sum(item.get("quantity", 0) for item in cart.values())
    return total_items


def catalog(request: HttpRequest):
    products = get_products()
    categories = list(dict.fromkeys(product["category"] for product in products))
    return render(request, "catalog.html", {"products": products, "categories": categories, "cart_count": cart_summary(request)})


def product_detail(request: HttpRequest, slug: str):
    products = get_products()
    product = next((item for item in products if item["slug"] == slug), None)
    if not product:
        return HttpResponse("No encontramos ese producto.", status=404)
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
    if not request.session.get("token"):
        messages.info(request, "Inicia sesión para finalizar tu compra y consultar tus pedidos.")
        return redirect("login")

    if request.method == "POST":
        cart = request.session.get("cart", {})
        if not cart:
            messages.error(request, "Tu carrito está vacío")
            return redirect("catalog")
        order_payload = {
            "items": [{"product_id": product_id, "quantity": details.get("quantity", 1)} for product_id, details in cart.items()],
            "shipping_address": request.POST.get("shipping_address", ""),
            "contact_phone": request.POST.get("contact_phone", "").strip(),
        }
        if not order_payload["shipping_address"].strip() or not order_payload["contact_phone"]:
            messages.error(request, "Escribe tu dirección y teléfono para continuar.")
            return redirect("checkout")
        try:
            response = requests.post(
                f"{API_URL}/api/orders",
                json=order_payload,
                headers={"Authorization": f"Bearer {request.session['token']}"},
                timeout=10,
            )
            if response.ok:
                request.session["cart"] = {}
                messages.success(request, "Tu pedido se creó correctamente.")
                return redirect("customer_account")
            if response.status_code == 401:
                request.session.pop("token", None)
                request.session.pop("user", None)
                messages.error(request, "Tu sesión venció. Inicia sesión para continuar.")
                return redirect("login")
        except requests.RequestException:
            messages.error(request, "No fue posible conectar con la tienda. Inténtalo de nuevo.")
            return redirect("checkout")
        messages.error(request, "No se pudo completar la compra. Inténtalo de nuevo.")
        return redirect("cart")
    return render(request, "checkout.html", {"cart_count": cart_summary(request)})


def login_view(request: HttpRequest, admin_only: bool = False):
    if request.method == "POST":
        payload = {"email": request.POST.get("email"), "password": request.POST.get("password")}
        try:
            response = requests.post(f"{API_URL}/api/auth/login", json=payload, timeout=10)
            data = response.json()
            if response.ok:
                if admin_only and not data["user"].get("is_admin"):
                    messages.error(request, "Esta cuenta no tiene permisos de administración.")
                    return render(
                        request,
                        "login.html",
                        {"cart_count": cart_summary(request), "admin_login": True},
                    )
                request.session["token"] = data["token"]
                request.session["user"] = data["user"]
                messages.success(request, "Inicio de sesión correcto")
                if data["user"].get("is_admin"):
                    return redirect("admin_dashboard")
                return redirect("customer_account")
            detail = data.get("detail", "")
            translated_errors = {
                "Invalid credentials": "El correo o la contraseña no son correctos.",
                "Authentication required": "Inicia sesión para continuar.",
                "Invalid token": "La sesión no es válida. Inicia sesión de nuevo.",
            }
            messages.error(request, translated_errors.get(detail, detail or "El correo o la contraseña no son correctos."))
        except requests.RequestException:
            messages.error(request, "No fue posible iniciar sesión. Inténtalo de nuevo.")
    return render(
        request,
        "login.html",
        {"cart_count": cart_summary(request), "admin_login": admin_only},
    )


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
            detail = data.get("detail", "")
            translated_errors = {
                "Email already registered": "Este correo ya tiene una cuenta registrada.",
                "Invalid email address": "El correo electrónico no es válido.",
            }
            messages.error(request, translated_errors.get(detail, detail or "No se pudo crear la cuenta."))
        except requests.RequestException:
            messages.error(request, "No fue posible crear la cuenta. Inténtalo de nuevo.")
    return render(request, "register.html", {"cart_count": cart_summary(request)})


def logout_view(request: HttpRequest):
    request.session.flush()
    messages.info(request, "Sesión cerrada")
    return redirect("catalog")


def customer_account(request: HttpRequest):
    user = request.session.get("user")
    token = request.session.get("token")
    if not user or not token:
        messages.info(request, "Inicia sesión para consultar tu cuenta y tus pedidos.")
        return redirect("login")

    try:
        response = requests.get(
            f"{API_URL}/api/orders/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if response.status_code == 401:
            request.session.pop("token", None)
            request.session.pop("user", None)
            messages.error(request, "Tu sesión venció. Inicia sesión de nuevo.")
            return redirect("login")
        response.raise_for_status()
        orders = response.json()
    except requests.RequestException:
        messages.error(request, "No fue posible cargar tus pedidos. Inténtalo de nuevo.")
        orders = []

    products = {product["id"]: product for product in get_products()}
    for order in orders:
        order["status"] = translate_order_status(order.get("status", "pendiente"))
        for item in order.get("items", []):
            product = products.get(item.get("product_id"))
            item["product_name"] = product["name"] if product else "Producto"

    return render(
        request,
        "customer_account.html",
        {"user": user, "orders": orders, "cart_count": cart_summary(request)},
    )


def translate_order_status(status: str) -> str:
    return {
        "pending": "Pendiente",
        "pendiente": "Pendiente",
        "processing": "En preparación",
        "shipped": "Enviado",
        "delivered": "Entregado",
        "cancelled": "Cancelado",
    }.get(status.lower(), status.capitalize())


def admin_dashboard(request: HttpRequest):
    user = request.session.get("user")
    token = request.session.get("token")
    if not user or not token:
        messages.info(request, "Inicia sesi?n con la cuenta de administraci?n.")
        return redirect("admin_login")
    if not user.get("is_admin"):
        messages.error(request, "Esta secci?n es exclusiva para administraci?n.")
        return redirect("customer_account")

    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_product":
            name = (request.POST.get("name") or "").strip()
            category = (request.POST.get("category") or "").strip()
            description = (request.POST.get("description") or "").strip()
            image_url = (request.POST.get("image_url") or "").strip()
            price_raw = request.POST.get("price", "0")
            try:
                price = float(price_raw)
            except (TypeError, ValueError):
                price = 0.0
            if not name or not category or not description or price <= 0:
                messages.error(request, "Completa nombre, categor?a, descripci?n y precio v?lido.")
            else:
                payload = {
                    "name": name,
                    "category": category,
                    "price": price,
                    "original_price": round(price * 1.2, 2),
                    "rating": 0.0,
                    "reviews": 0,
                    "image_url": image_url or "https://images.unsplash.com/photo-1521369909026-2afc9123a8c7?auto=format&fit=crop&w=1200&q=80",
                    "in_stock": request.POST.get("in_stock") == "on",
                    "description": description,
                    "features": [item.strip() for item in request.POST.get("features", "").split(",") if item.strip()],
                    "tags": [category.lower()],
                }
                try:
                    response = requests.post(f"{API_URL}/api/products", json=payload, headers=headers, timeout=10)
                    if response.ok:
                        messages.success(request, "Producto a?adido correctamente.")
                    else:
                        details = response.json()
                        messages.error(request, details.get("detail", "No se pudo crear el producto."))
                except requests.RequestException:
                    messages.error(request, "No fue posible crear el producto. Int?ntalo de nuevo.")
        elif action == "delete_product":
            product_id = request.POST.get("product_id", "").strip()
            if not product_id:
                messages.error(request, "No se indic? el producto a eliminar.")
            else:
                try:
                    response = requests.delete(f"{API_URL}/api/products/{product_id}", headers=headers, timeout=10)
                    if response.ok:
                        messages.success(request, "Producto eliminado correctamente.")
                    else:
                        details = response.json()
                        messages.error(request, details.get("detail", "No se pudo eliminar el producto."))
                except requests.RequestException:
                    messages.error(request, "No fue posible eliminar el producto. Int?ntalo de nuevo.")

    try:
        summary_response = requests.get(f"{API_URL}/api/admin/summary", headers=headers, timeout=10)
        summary_response.raise_for_status()
        orders_response = requests.get(f"{API_URL}/api/orders", headers=headers, timeout=10)
        orders_response.raise_for_status()
        products_response = requests.get(f"{API_URL}/api/products", headers=headers, timeout=10)
        products_response.raise_for_status()
        stats = summary_response.json()
        orders = orders_response.json()
        products = products_response.json()
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 401:
            request.session.pop("token", None)
            request.session.pop("user", None)
            messages.error(request, "Tu sesi?n venci?. Inicia sesi?n de nuevo.")
            return redirect("admin_login")
        messages.error(request, "No tienes permiso para consultar la administraci?n.")
        return redirect("customer_account")
    except requests.RequestException:
        messages.error(request, "No fue posible cargar la informaci?n de administraci?n.")
        stats = None
        orders = []
        products = []

    product_map = {product["id"]: product for product in get_products()}
    for order in orders:
        order["status"] = translate_order_status(order.get("status", "pendiente"))
        for item in order.get("items", []):
            product = product_map.get(item.get("product_id"))
            item["product_name"] = product["name"] if product else "Producto"

    return render(
        request,
        "admin_dashboard.html",
        {"stats": stats, "orders": orders, "products": products, "cart_count": cart_summary(request)},
    )
