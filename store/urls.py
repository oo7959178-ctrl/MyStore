from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # --- 1. الحسابات والمستخدمين ---
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # --- 2. المتجر والمنتجات ---
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # --- 3. سلة التسوق ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # --- 4. الدفع والطلبات ---
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/cod/', views.cod_checkout, name='cod_checkout'),
    path('checkout/edahabia/', views.edahabia_payment, name='edahabia_payment'),
    path('payment-ccp/', views.ccp_checkout, name='ccp_checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # --- 5. السياسات القانونية ---
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),

    # --- 6. إعدادات إضافية ---
    path('i18n/', include('django.conf.urls.i18n')),
]

# خدمة ملفات الميديا (Media Files) في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)