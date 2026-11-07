from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/<str:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<str:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("login/", views.login_view, name="login"),
    path("admin-login/", views.login_view, {"admin_only": True}, name="admin_login"),
    path("register/", views.register_view, name="register"),
    path("mi-cuenta/", views.customer_account, name="customer_account"),
    path("logout/", views.logout_view, name="logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
