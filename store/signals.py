import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def notify_new_order_telegram(sender, instance, created, **kwargs):
    if created: 
        # التوكن الخاص بالبوت
        bot_token = '8991816941:AAG36mMuQqh9VarOcVOw70rLpCDGJSeBf7M'
        
        # استبدل الرقم هنا بالـ ID الخاص بك
        chat_id = '6497250191'   

        # تجهيز نص الرسالة
        message = f'''
        🚀 طلب جديد تم استلامه!
        
        رقم الطلب: #{instance.id}
        الاسم الكامل: {instance.client_name}
        رقم الهاتف: {instance.client_phone}
        الولاية: {instance.client_state}
        المدينة/البلدية: {instance.client_city}
        طريقة الدفع: {instance.get_payment_method_display()} 
        ملاحظات: {instance.note}
        '''
        
        # إرسال الرسالة مع ضبط وقت انتظار (timeout) لمنع تعليق الموقع
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': message
        }
        
        try:
            # إضافة timeout لضمان عدم توقف المتجر إذا كان سيرفر تيليجرام بطيئاً
            requests.post(url, data=data, timeout=5)
        except Exception as e:
            print(f"حدث خطأ أثناء إرسال إشعار تيليجرام: {e}")