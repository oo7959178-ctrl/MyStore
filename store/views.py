import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Product, Category

# إعداد مفتاح سترايب السري
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
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
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
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
        if method == 'stripe':
            return create_checkout_session(request)
        elif method == 'ccp':
            return redirect('ccp_checkout')
        elif method == 'cod':
            return redirect('cod_checkout') 
            
    return JsonResponse({'error': 'طريقة دفع غير صحيحة'}, status=400)


# --- 5. بوابة دفع Stripe التلقائية ---
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'error': 'السلة فارغة'}, status=400)
    
    line_items = []
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        line_items.append({
            'price_data': {
                'currency': 'usd', 
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100), 
            },
            'quantity': quantity,
        })

    try:
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            payment_method='visa',
            status='تم الدفع (Stripe)'
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            client_reference_id=order.id, 
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('client_reference_id')
        stripe_payment_id = session.get('payment_intent') or session.get('id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'Paid'
                order.transaction_id = stripe_payment_id
                order.save()
            except Order.DoesNotExist:
                pass
                
    return HttpResponse(status=200)

@login_required(login_url='login')
def payment_success(request):
    if 'cart' in request.session:
        del request.session['cart']
    return render(request, 'store/success.html')


# --- 6. بوابة دفع البطاقة الذهبية CCP ---
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


# --- 7. بوابة الدفع عند الاستلام COD ---
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


# --- 8. دوال إضافية وصفحات فرعية ---
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