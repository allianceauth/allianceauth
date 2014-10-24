"""
Django settings for alliance_auth project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery
djcelery.setup_loader()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5xvh4e0x&@-$6(kj%4^80pdo1n5v-!mtx(e(1tw@kn-1le*ts@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

BROKER_URL = 'amqp://guest:guest@localhost:5672/'

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# EMAIL SETTINGS
# By default uses the python smtpd server
DOMAIN = 'https://the99eve.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_evolution',
    'djcelery',
    'celerytask',
    'bootstrapform',
    'authentication',
    'portal',
    'registration',
    'services',
    'eveonline',
    'groupmanagement'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'alliance_auth.urls'

WSGI_APPLICATION = 'alliance_auth.wsgi.application'

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
    'util.context_processors.alliance_name',
    'util.context_processors.jabber_url',
    'util.context_processors.domain_url'
)

TEMPLATE_DIRS = (
    'templates',
)

STATICFILES_DIRS = (
    'static',
)

LOGIN_URL = '/login_user/'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

DEFAULT_ALLIANCE_GROUP = 'AllianceMember'

# ALLIANCE INFO
ALLIANCE_ID = '0'
ALLIANCE_NAME = 'Somealliance'

# Forum URL
FORUM_URL = "http://someaddress.com"

# Jabber Prosody Info
JABBER_URL = "someaddress.com"
JABBER_PORT = 5223
JABBER_SERVER = "someadddress.com"
OPENFIRE_ADDRESS = "http://someaddress.com:9090/"
OPENFIRE_SECRET_KEY = "somekey"

BROADCAST_USER = "broadcast@"+JABBER_URL
BROADCAST_USER_PASSWORD = "somepassword"

# Mumble settings
MUMBLE_URL = "someurl.com"
MUMBLE_SERVER_ID = 1

