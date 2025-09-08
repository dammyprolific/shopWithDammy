from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-default-dev-secret-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') != 'False'  # Default True for dev; set to 'False' in prod

ALLOWED_HOSTS = [
    "shopwithdammy2.onrender.com",
    "localhost",
    "127.0.0.1",
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Local apps
    'coreUsers',
    'Shopping_App',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ShopWithDammy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ShopWithDammy.wsgi.application'

# Database (local PostgreSQL config)
# Database
# Use DATABASE_URL from environment (for Render), fallback to local settings (for local dev)

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    raise Exception("❌ DATABASE_URL environment variable is not set. Please add it in the Render Dashboard.")

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'Ecommerce_db'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'function14'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files config
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files config
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL = "coreUsers.CustomUsers"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Base URLs for frontend or API calls
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
REACT_BASE_URL = os.environ.get("REACT_BASE_URL", "http://localhost:5173")

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Consider setting to False in production for security

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://shop-c9zj.onrender.com",
]

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
}

# Payment gateways - set these in environment variables for security
FLUTTERWAVE_SECRET_KEY = os.environ.get('FLUTTERWAVE_SECRET_KEY', 'FLWSECK_TEST-5178b0f76422f10d30d9457cb284a344-X')

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "ARWe8mgWX6U5lYZOA2_eCEdCqn626MAykueQ0Chug-VqNDgJiIMlS5QrBRvr_Hh1R9KDlHpAeU0d3aC0")
PAYPAL_SECRET_KEY = os.environ.get("PAYPAL_SECRET_KEY", "EBrLuxHP_VZUz7tMGKtDDprzV1yps3wIHXQzXwS_PAaOr77_CYFxZWv50fmmbnpWFaKdDnEBcX3WOWY5")
PAYPAL_MODE = 'live'  # Change to 'sandbox' for testing

REACT_BASE_URL = os.getenv("REACT_BASE_URL", "http://localhost:5173")
