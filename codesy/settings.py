"""
Django settings for codesy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os

import dj_database_url
from decouple import config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='terrible-secret-for-travis')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'corsheaders',
    'mailer',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
)

LOCAL_APPS = (
    'codesy.base',
    'api',
    'auctions',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'codesy.context_processors.conf_settings',
    'codesy.context_processors.current_site',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'codesy/templates'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# auth and allauth settings
ACCOUNT_ADAPTER = 'codesy.adapters.CodesyAccountAdapter'
ACCOUNT_EMAIL_VERIFICATION = config('ACCOUNT_EMAIL_VERIFICATION',
                                    default='optional')
AUTH_USER_MODEL = 'base.User'
# OAuth2View uses this for the callback_url protocol
ACCOUNT_DEFAULT_HTTP_PROTOCOL = config(
    'ACCOUNT_DEFAULT_HTTP_PROTOCOL', default='http')
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_ADAPTER = 'codesy.adapters.CodesySocialAccountAdapter'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': ['user:email'],
    }
}

ROOT_URLCONF = 'codesy.urls'

WSGI_APPLICATION = 'codesy.wsgi.application'

DATABASES = {'default': config(
    'DATABASE_URL',
    default="postgres://postgres@localhost:5432/codesy",
    cast=dj_database_url.parse)}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

SITE_ID = 1

TEST_RUNNER = config('TEST_RUNNER',
                     default='django.test.runner.DiscoverRunner')

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES':
        ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': 10
}

SWAGGER_SETTINGS = {
    'exclude_namespaces': ['single_bid']
}

DEFAULT_FROM_EMAIL = 'codesy notifications <notifications@codesy.io>'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = config('SENDGRID_USERNAME', default='')
EMAIL_HOST_PASSWORD = config('SENDGRID_PASSWORD', default='')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Payment provider settings
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')   # sandbox or live
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_PAYOUT_RECIPIENT = config('PAYPAL_PAYOUT_RECIPIENT', default='')
# TODO: create PAYPAL_SANDBOX_CLIENT_SECRET in .env
