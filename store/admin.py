from django.contrib import admin
from .models import Order, Product, Category, Review, ProductImage

# إعداد خانات الرفع المتعدد للصور داخل صفحة المنتج
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # عدد الخانات الفارغة التي تظهر لك تلقائياً لإضافة صور جديدة

# 1. تسجيل المنتجات
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'video')
    inlines = [ProductImageInline]

# 2. تسجيل التصنيفات والمراجعات (بدون Order)
admin.site.register(Category)
admin.site.register(Review)

# 3. تسجيل الطلبات (مرة واحدة فقط هنا)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_method', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'transaction_id')