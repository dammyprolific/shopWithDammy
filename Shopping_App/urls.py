from django.urls import path
from . import views 

urlpatterns = [
    path("Products/", views.get_products, name="Products"),
    path("product-detail/<slug:slug>/", views.get_product_detail, name="product-detail"),
    path("add_item/", views.add_item, name="add_item"),
    path("check_product_in_cart/", views.check_product_in_cart, name="check_product_in_cart"),
    path("get_cart_stat/", views.get_cart_stat, name="get_cart_stat"),
    path("get_cart/", views.get_cart, name="get_cart"),
    path("update_quantity/", views.update_quantity, name="update_quantity"),
    path("delete_cartitem/<int:item_id>/", views.delete_cartitem, name="delete_cartitem"),
    path("get_username/", views.get_username, name="get_username"),
    path("user_info/", views.user_info, name="user_info"),
    path("initiate_payment/", views.initiate_payment, name="initiate_payment"),
    path("payment_callback/", views.payment_callback, name="payment_callback"),
    path("initiate_paypal_payment/", views.initiate_paypal_payment, name="initiate_paypal_payment"),
    path("paypal_payment_callback/", views.paypal_payment_callback, name="paypal_payment_callback"),
    path("create_user/", views.create_user, name="create_user"),
    path("Products-list/", views.ProductsListView.as_view(), name="Products-list"),
]


