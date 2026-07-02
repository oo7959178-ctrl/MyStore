from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # تعديل الكلمة هنا إلى urls
    path('', include('store.urls')),  # الربط بتطبيق store
]

# السماح بقراءة صور المنتجات أثناء التطوير المحلي
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)