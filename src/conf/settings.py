"""
Django settings for conf project.

Generated by 'django-admin startproject' using Django 3.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
import datetime

from environs import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', 1)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'constance',
    'django_filters',
    'django_celery_beat',
    'corsheaders',
    'django_admin_inline_paginator',

    # My apps
    'apps.core.apps.CoreConfig',
    'apps.api.apps.ApiConfig',
    'apps.etl.apps.EtlConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'conf.urls'

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

WSGI_APPLICATION = 'conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_NAME'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST'),
        'PORT': env.str('POSTGRES_PORT'),
    },
    'source': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('MYSQL_NAME'),
        'USER': env.str('MYSQL_USER'),
        'PASSWORD': env.str('MYSQL_PASSWORD'),
        'HOST': env.str('MYSQL_HOST'),
        'PORT': env.str('MYSQL_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis
REDIS_HOST = env.str('REDIS_HOST')
REDIS_DB = env.str('REDIS_DB')
REDIS_PORT = env.int('REDIS_PORT')

# Celery
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'PAGE_SIZE': 10,
}

SILENCED_SYSTEM_CHECKS = [
    "rest_framework.W001",
]

if env.bool('DJANGO_USE_HTTPS', 1):
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


def handler_file(level: str, filename: str) -> Dict[str, Any]:
    return {
        'level': level,
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs', filename),
        'maxBytes': 1024 * 1024 * 500,  # 500 MB
        'backupCount': 7,
        'formatter': 'verbose',
        'encoding': 'utf8',
    }.copy()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {name} {asctime} {module} {process:d} {thread:d} {filename}:{lineno} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'stream': sys.stdout, 'formatter': 'verbose'},
        'error_file': handler_file('ERROR', 'error.log'),
    },
    'root': {'handlers': ['console', 'error_file'], 'level': 'ERROR'},
}

CONSTANCE_REDIS_CONNECTION = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
}

CONSTANCE_CONFIG = {
    'STRATEGIC_SOURCE_TABLENAME': (
        'freedomapp_export_to_excel',
        'Таблица со страт задачами в mysql-бд'
    ),
    'OPERATIONAL_SOURCE_TABLENAME': (
        'freedomapp_export_to_excel_og',
        'Таблица с опер задачами в mysql-бд'
    ),
    'SYNCHRONIZATION_INTERVAL': (24, 'Промежуточные часы между запуском синхронизации'),
    'SYNCHRONIZATION_RETRIES_COUNT': (3, 'Количество попыток синхронизации данных из бд'),
    'SUP_ADMIN_EMAIL': ('test@gmail.com', 'Электронная почта администратора sup для уведомления'),
    'CONTROL_PERIOD_IN_DAYS': (30, 'Контрольный период'),
    'LAST_SYNC_DATE': (datetime.date(2022, 7, 27), 'Дефолтная значения даты последний синхронизации'),
    'MAX_OPERATIONAL_TASK_ON_STRATEGIC_TASK': (10, 'Максимальное количество операционных задач '
                                                   'внутри стратегической'),
    'INITIAL_DATA_NAMES': (
        "{"
        "   'area_name': 'Неопределенный регион', "
        "   'project_name': 'Неопределенный проект', "
        "   'gp_name': 'Неопределенный ГП', "
        "   'section_name': 'Неопределенная секция', "
        "   'strategic_task_name': 'Неопределенная стратегическая задача', "
        "   'archived_strategic_task_name': 'Неопределенная архивная стратегическая задача'"
        "}",
        'Названии для тестовых данных'
    ),
}
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

# SMTP
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_USE_TLS = env.str('EMAIL_USE_TLS')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

try:
    from conf.local_settings import *  # noqa: F401, F403
except ImportError:
    pass
