import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order # تأكد من أن اسم المودل مطابق لما لديك

@receiver(post_save, sender=Order)
def notify_new_order_telegram(sender, instance, created, **kwargs):
    if created: 
        # التوكن الخاص بالبوت الذي أنشأته
        bot_token = '8991816941:AAG36mMuQqh9VarOcVOw70rLpCDGJSeBf7M'
        
        # استبدل هذه القيمة بالرقم الذي حصلت عليه من userinfobot
        chat_id = '6497250191'   

        # تجهيز نص الرسالة
        message = f'''
        🚀 طلب جديد تم استلامه!
        
        رقم الطلب: #{instance.id}
        الاسم: {instance.full_name}
        رقم الهاتف: {instance.phone}
        الولاية: {instance.state}
        المدينة/البلدية: {instance.city}
        '''
        
        # إرسال الرسالة عبر API تيليجرام
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': message
        }
        
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"حدث خطأ أثناء إرسال إشعار تيليجرام: {e}")