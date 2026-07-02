from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .models import Order
from .models import Product
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

from .models import Product, Category # تأكد من استيراد كلاهما في الأعلى
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
def profile(request):
    return render(request, 'registration/profile.html') # سننشئ هذا الملف لاحق

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # تسجيل الدخول تلقائياً بعد إنشاء الحساب
            return redirect('home') # التوجه للرئيسية
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
@login_required(login_url='login') # تحويل المستخدم لصفحة الدخول إذا لم يكن مسجلاً
def my_orders(request):
    # فلترة الطلبات بناءً على المستخدم الحالي
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders
    }
    return render(request, 'my_orders.html', context)
def process_payment(request):
    if request.method == 'POST':
        method = request.POST.get('payment_method')
        
        if method == 'stripe':
            return create_checkout_session(request)
        elif method == 'ccp':
            return redirect('ccp_checkout')
        elif method == 'cod': # الخيار الجديد
            return redirect('cod_checkout') 
            
    return JsonResponse({'error': 'طريقة دفع غير صحيحة'}, status=400)
# في ملف views.py
@login_required  # تأكد أنك تستخدم هذا الديكوريتور لإجبار المستخدم على تسجيل الدخول
def payment_ccp(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        
        # إنشاء الطلب وربطه بالمستخدم الحالي
        new_order = Order.objects.create(
            user=request.user,  # <--- هذا هو السطر الأهم لربط الطلب بك
            status='قيد المراجعة',
            transaction_id=transaction_id
            # أضف باقي الحقول الخاصة بطلبك هنا
        )
        new_order.save()
        return redirect('my_orders') # توجيه المستخدم لصفحة طلباته بعد الدفع
    
    return render(request, 'ccp_checkout.html')
def home(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '') # جلب رقم التصنيف إذا ضغط عليه العميل
    
    products = Product.objects.all()
    categories = Category.objects.all() # جلب كل التصنيفات لعرضها كأزرار
    
    # الفلترة بالبحث
    if search_query:
        products = products.filter(name__icontains=search_query)
        
    # الفلترة بالتصنيف
    if category_id:
        products = products.filter(category_id=category_id)
        
    context = {
        'products': products,
        'categories': categories,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id.isdigit() else '', # لمعرفة التصنيف النشط حالياً
    }
    return render(request, 'store/home.html', context)
# 2. صفحة تفاصيل المنتج والتقييمات
# store/views.py

def create_checkout_session(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return JsonResponse({'error': 'السلة فارغة'}, status=400)
    
    line_items = []
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        line_items.append({
            'price_data': {
                'currency': 'usd', # تأكد أنها نفس العملة في لوحة تحكم Stripe
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100), # السعر بالسنت
            },
            'quantity': quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all() if hasattr(product, 'reviews') else []
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)
# 3. إضافة منتج للسلة
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    return redirect('cart_detail')

# 4. عرض صفحة السلة
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue
            
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'store/cart.html', context)

# 5. حذف منتج من السلة
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        
    return redirect('cart_detail')

# 6. إنشاء جلسة الدفع عبر Stripe للسلة بالكامل
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # تأكد من وجود هذا الاستيراد

# فقط احتفظ بهذا الجزء للدالة
@login_required 
def ccp_checkout(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        
        new_order = Order.objects.create(
            user=request.user,
            status='قيد المراجعة',
            transaction_id=transaction_id
        )
        new_order.save()
        
        # تنظيف السلة
        if 'cart' in request.session:
            del request.session['cart']
            
        messages.success(request, 'تم استلام طلبك!')
        return redirect('my_orders')
    
    return render(request, 'ccp_checkout.html')
@login_required
def cod_checkout(request):
    if request.method == 'POST':
        # إنشاء الطلب
        new_order = Order.objects.create(
            user=request.user,
            status='قيد المراجعة',
            payment_method='cod', # تأكد أن هذا الخيار موجود في خيارات الموديل
            transaction_id='نقد'
        )
        new_order.save() # هذا السطر هو ما يرسل البيانات لقاعدة البيانات
        
        # تفريغ السلة
        if 'cart' in request.session:
            del request.session['cart']
            
        messages.success(request, 'تم استلام طلبك بنجاح!')
        return redirect('my_orders') # توجيه الزبون لصفحة طلباته
    
    return render(request, 'ccp_checkout.html') #أو أي صفحة تريدها ح

# 7. صفحة نجاح الدفع وتنظيف السلة
from django.contrib.auth.decorators import login_required

@login_required # تأكد من إضافة هذا ليعرف النظام من هو الزبون
def payment_success(request):
    # 1. إنشاء الطلب وربطه بالمستخدم بعد نجاح الدفع في سترايب
    new_order = Order.objects.create(
        user = request.user,
        status = 'تم الدفع (Stripe)', # لكي تميزه في لوحة التحكم
        transaction_id = 'دفع إلكتروني' # يمكننا لاحقاً جلب رقم العملية الحقيقي من سترايب
    )
    new_order.save()

    # 2. تفريغ السلة بعد حفظ الطلب
    if 'cart' in request.session:
        del request.session['cart']
        
    return render(request, 'store/success.html')

# 8. صفحات السياسات القانونية لـ Stripe
def privacy_policy(request):
    return render(request, 'store/policies/privacy.html')

def terms_of_service(request):
    return render(request, 'store/policies/terms.html')

def refund_policy(request):
    return render(request, 'store/policies/refund.html')
def checkout(request):
    # لاحقاً سنضيف هنا أكواد معالجة الدفع وتفريغ السلة
    return render(request, 'store/checkout.html')
def edahabia_payment(request):
    return render(request, 'edahabia_payment.html')