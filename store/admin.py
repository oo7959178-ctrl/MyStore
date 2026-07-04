from django.contrib import admin
from .models import Order, Product, Category, Review, ProductImage  # تم إضافة ProductImage هنا

# إعداد خانات الرفع المتعدد للصور داخل صفحة المنتج
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # عدد الخانات الفارغة التي تظهر لك تلقائياً لإضافة صور جديدة


# 1. تسجيل المنتجات (بطريقة الديكوريتور @)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # أضف اسم الحقل 'video' هنا ليظهر في لوحة التحكم
    list_display = ('name', 'price', 'video')
    inlines = [ProductImageInline]  # تم دمج معرض الصور المتعددة هنا بنجاح


# 2. تسجيل المودلز الأخرى (بطريقة مباشرة لأننا لا نحتاج كلاس مخصص لها حالياً)
admin.site.register(Category)
admin.site.register(Review)


# 3. تسجيل الطلبات
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_method', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'transaction_id')