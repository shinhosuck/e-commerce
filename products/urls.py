from django.urls import path 
from .views import (
    home_view,
    product_list_view,
    product_detail_view,
    product_create_view,
    write_product_review_view,
    product_search_view,
    add_to_basket_view,
    basket_view,
    update_basket_view,
    customer_address_view,
    checkout_summary_view,
    checkout_view,
    create_checkout_session_view,
    payment_cancel_view,
    payment_success_view,
    stripe_webhook,
    order_history_view,
    success_view,
    email_receipt_view
)


app_name = 'products'



urlpatterns = [
    path('', home_view, name='product-home'),
    path('products/', product_list_view, name='product-list'),
    path('product/create/', product_create_view, name='product-create'),
    path('product/<uuid:id>/detail/', product_detail_view, name='product-detail'),
    path('product/<uuid:id>/review/',write_product_review_view, name='product-review' ),
    path('product/search/', product_search_view, name='product-search'),
    path('product/<uuid:id>/add-to-basket/', add_to_basket_view, name='add-to-basket'),
    path('my/basket/', basket_view, name='product-basket'),
    path('update/<str:id>/qty', update_basket_view, name='update-basket'),
    path('shipping/address/', customer_address_view, name='shipping-address'),
    path('checkout/summary/', checkout_summary_view, name='checkout-summary'),
    path('checkout/', checkout_view, name='checkout'),
    path('create/checkout/session/<uuid:id>/', create_checkout_session_view, name='checkout-session'),
    path('payment/success/<uuid:id>/', payment_success_view, name='payment-success'),
    path('payment/cancel/', payment_cancel_view, name='payment-cancel'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('order/history/', order_history_view, name='order-history'),
    path('payment/success/', success_view, name='success'),
    path('email/receipt/<uuid:id>/', email_receipt_view, name='email-receipt'),
]