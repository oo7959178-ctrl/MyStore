import os
import dj_database_url
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-&e0e&bcdybm_@*o@&x*&2ycmww=x%=fxhw4(#n&uqg#a*(i2=+')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*', 'mystore-9kma.onrender.com']

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev',
    'https://*.ngrok-free.app',
    'https://mystore-9kma.onrender.com',
]

INSTALLED_APPS = [
    'cloudinary_storage',
    'cloudinary',
    'store',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'store', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

LANGUAGES = [('ar', 'Arabic'), ('en', 'English')]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 1. الإعدادات الحديثة (هذه هي المسؤولة عن تشغيل الموقع)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# 2. إعداد إضافي (للخداع فقط) لإسكات المكتبة ومنع خطأ AttributeError
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# بيانات ربط Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

try:
    from local_settings import *
except ImportError:
    pass