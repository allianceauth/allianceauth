"""
Django settings for allianceauth project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g1l84fup$w7nd!cczv!3vkht^5a6&t2g&*hd^*b!ap=9x)7rdd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_evolution',
    'bootstrapform',
    'authentication',
    'portal',
    'registration',
    'evespecific',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'allianceauth.urls'

WSGI_APPLICATION = 'allianceauth.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_auth',
        'USER': 'allianceauth',
        'PASSWORD': 'allianceauth',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    
    'phpbb3': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_forum',
        'USER': 'allianceauth',
        'PASSWORD': 'allianceauth',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },

    'mumble': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_mumble',
        'USER': 'allianceauth',
        'PASSWORD': 'allianceauth',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'util.context_processors.alliance_id',
    'util.context_processors.alliance_name'
)

########## USER CONFIGURATION
AUTH_USER_MODEL = 'authentication.AllianceUser'
########## END USER CONFIGURATION

LOGIN_URL = '/login_user/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

TEMPLATE_DIRS = (
    'templates',
)

STATICFILES_DIRS = (
    'static',
)

STATIC_URL = '/static/'

# ALLIANCE INFO
ALLIANCE_ID = 'someid'
ALLIANCE_NAME = 'somealliancename'

# Jabber Prosody Info
OPENFIRE_ADDRESS = "http://someaddres.com:9090/"
OPENFIRE_SECRET_KEY = "somesecretkey"

# Mumble settings
MUMBLE_SERVER_ID = 1