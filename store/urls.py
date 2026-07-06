from django.urls import path
from . import views
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # روابط سلة التسوق
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('success/', views.payment_success, name='payment_success'),
    
    # روابط السياسات القانونية
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    # ... مساراتك الأخرى الموجودة مسبقاً ...
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-ccp/', views.ccp_checkout, name='ccp_checkout'),
    # ... مساراتك الأخرى هنا ...
    path('my-orders/', views.my_orders, name='my_orders'),
    path('checkout/edahabia/', views.edahabia_payment, name='edahabia_payment'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('checkout/cod/', views.cod_checkout, name='cod_checkout'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('i18n/', include('django.conf.urls.i18n')),
   
]
from django.conf import settings
from django.conf.urls.static import static

# في نهاية ملف urls.py أضف:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)