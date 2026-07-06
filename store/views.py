from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Order, Product, Category

# --- 1. الحسابات والمستخدمين ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    return render(request, 'registration/profile.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'my_orders.html', {'orders': orders})


# --- 2. المتجر والرئيسية وتفاصيل المنتجات ---
def home(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    categories = Category.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query) 
    if category_id:
        products = products.filter(category_id=category_id)
        
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id.isdigit() else '',
    }
    return render(request, 'store/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all() if hasattr(product, 'reviews') else []
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


# --- 3. نظام سلة التسوق ---
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    return redirect('cart_detail')


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
    }
    return render(request, 'store/cart.html', context)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        
    return redirect('cart_detail')


# --- 4. معالجة وتوجيه طرق الدفع ---
def process_payment(request):
    if request.method == 'POST':
        method = request.POST.get('payment_method')
        if method == 'ccp':
            return redirect('ccp_checkout')
        elif method == 'cod':
            return redirect('cod_checkout') 
            
    return JsonResponse({'error': 'طريقة دفع غير صحيحة'}, status=400)


# --- 5. بوابة دفع البطاقة الذهبية CCP ---
@login_required(login_url='login')
def ccp_checkout(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "سلتك فارغة حالياً!")
            return redirect('cart_detail')

        if not transaction_id:
            messages.error(request, "الرجاء إدخال رقم العملية لتأكيد الدفع.")
            return render(request, 'ccp_checkout.html')
        
        Order.objects.create(
            user=request.user,
            status='قيد المراجعة',
            payment_method='ccp',
            transaction_id=transaction_id
        )
        
        if 'cart' in request.session:
            del request.session['cart']
            
        messages.success(request, 'تم استلام بيانات تحويل الـ CCP بنجاح وجاري مراجعة طلبك!')
        return redirect('my_orders')
    
    return render(request, 'ccp_checkout.html')


# --- 6. بوابة الدفع عند الاستلام COD ---
@login_required(login_url='login')
def cod_checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "سلتك فارغة حالياً!")
        return redirect('cart_detail')

    if request.method == 'POST':
        # 👇 استقبال البيانات الأربعة الجديدة المرسلة من الـ Javascript 👇
        client_name = request.POST.get('name')
        client_phone = request.POST.get('phone')
        client_state = request.POST.get('state')
        client_city = request.POST.get('city')

        # إنشاء الطلب وتخزين البيانات داخله
        Order.objects.create(
            user=request.user,
            status='قيد المراجعة',
            payment_method='cod',
            transaction_id='الدفع عند الاستلام',
            # 👇 ربط البيانات المستلمة بحقول موديل الـ Order 👇
            client_name=client_name,
            client_phone=client_phone,
            client_state=client_state,
            client_city=client_city
        )
        
        if 'cart' in request.session:
            del request.session['cart']
            
        messages.success(request, 'تم تسجيل طلبك بنجاح! سيتم الدفع والتوصيل فوراً.')
        return redirect('my_orders')
    
    return render(request, 'store/checkout.html')


# --- 7. دوال إضافية وصفحات فرعية ---
@login_required(login_url='login')
def payment_success(request):
    if 'cart' in request.session:
        del request.session['cart']
    return render(request, 'store/success.html')

def checkout(request):
    return render(request, 'store/checkout.html')

def edahabia_payment(request):
    return render(request, 'edahabia_payment.html') 

def privacy_policy(request):
    return render(request, 'store/policies/privacy.html')

def terms_of_service(request):
    return render(request, 'store/policies/terms.html')

def refund_policy(request):
    return render(request, 'store/policies/refund.html')