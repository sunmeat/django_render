import os
import dj_database_url
from pathlib import Path

# ====================== BASE ======================
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================== Завантаження .env файлу ======================
try:
    from dotenv import load_dotenv
    load_dotenv()  # Автоматично шукає .env у корені проєкту
    print("✅ .env файл успішно завантажено")
except ImportError:
    print("⚠️ python-dotenv не встановлений. Встанови командою: pip install python-dotenv")

# ====================== SECRET KEY ======================
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise Exception("❌ SECRET_KEY не знайдено! Перевірте файл .env")

# ====================== DEBUG ======================
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# ====================== ALLOWED HOSTS ======================
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ====================== INSTALLED APPS ======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонні додатки
    'corsheaders',
    'django_filters',
    'rest_framework',

    # Ваші додатки
    'app',
    'api',
]

# ====================== MIDDLEWARE ======================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ====================== URL та WSGI ======================
ROOT_URLCONF = 'Rest.urls'
WSGI_APPLICATION = 'Rest.wsgi.application'

# ====================== DATABASE (PostgreSQL на Render + SQLite локально) ======================
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    # Локальна розробка
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ====================== TEMPLATES ======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# ====================== REST FRAMEWORK ======================
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.DefaultCursorPagination',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10000/day',
        'user': '10000/day',
    },

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# ====================== STATIC FILES ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ====================== CORS ======================
CORS_ALLOW_ALL_ORIGINS = True   # На продакшені краще обмежити

# ====================== SECURITY (Production) ======================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ====================== INTERNATIONALIZATION ======================
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ====================== CACHE ======================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}