# داخل ملف: store/apps.py

from django.apps import AppConfig

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store' # اسم التطبيق الخاص بك

    # أضف هذه الدالة هنا
    def ready(self):
        # نقوم باستيراد ملف الإشارات لكي يتعرف عليه جانغو
        import store.signals