from django.db import models
from django.contrib.auth.models import User 

# خيارات الدفع
PAYMENT_CHOICES = (
    ('visa', 'بطاقة عالمية (Visa / MasterCard)'),
    ('ccp', 'البطاقة الذهبية (CCP)'),
    ('cod', 'الدفع عند الاستلام'),
)

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    video = models.FileField(upload_to='products/videos/', blank=True, null=True) # تم دمج حقل الفيديو
    description = models.TextField(blank=True, null=True, verbose_name="وصف المنتج")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="التصنيف")
    stock = models.IntegerField(default=10)  # حقل كمية المخزون المتبقية

    def __str__(self):
        return self.name

# --- الموديل الجديد المضاف لرفع صور متعددة للمنتج الواحد ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="المنتج")
    image = models.ImageField(upload_to='products/gallery/', verbose_name="صورة إضافية")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة للمنتج"
        verbose_name_plural = "معرض صور المنتجات"

    def __str__(self):
        return f"صورة إضافية لـ {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='visa', verbose_name="طريقة الدفع")
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 👇 الحقول الجديدة المضافة لاستقبال بيانات شحن الدفع عند الاستلام 👇
    client_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="الاسم الكامل")
    client_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الهاتف")
    client_state = models.CharField(max_length=100, blank=True, null=True, verbose_name="الولاية")
    client_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="المدينة / البلدية")
    note = models.TextField(blank=True, null=True) # حقل الملاحظات

    def __str__(self):
        return f"طلب #{self.id} - {self.user.username if self.user else 'زائر'}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100, verbose_name="اسم العميل")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="التقييم")
    comment = models.TextField(verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.product.name} ({self.rating}★)"