from .base import *

# These are required for Django to function properly
ROOT_URLCONF = '{{ project_name }}.urls'
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]
STATIC_ROOT = "/var/www/{{ project_name }}/static/"
TEMPLATES[0]['DIRS'] += [os.path.join(PROJECT_DIR, 'templates')]
SECRET_KEY = '{{ secret_key }}'

# Change this to change the name of the auth site
SITE_NAME = '{{ project_name }}'

# Change this to enable/disable debug mode
DEBUG = False

#######################################
#         Database Settings           #
#######################################
# Uncomment and change the database name
# and credentials to use MySQL/MariaDB.
# Leave commented to use sqlite3
#######################################
"""
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'alliance_auth',
    'USER': os.environ.get('AA_DB_DEFAULT_USER', ''),
    'PASSWORD': os.environ.get('AA_DB_DEFAULT_PASSWORD', ''),
    'HOST': os.environ.get('AA_DB_DEFAULT_HOST', '127.0.0.1'),
    'PORT': os.environ.get('AA_DB_DEFAULT_PORT', '3306'),
}
"""

######################################
#            SSO Settings            #
######################################
# Register an application at
# https://developers.eveonline.com
# and fill out these settings.
# Be sure to set the callback URL to
# https://example.com/sso/callback
# substituting your domain for example.com
######################################
ESI_SSO_CLIENT_ID = ''
ESI_SSO_CLIENT_SECRET = ''
ESI_SSO_CALLBACK_URL = ''

######################################
#           Email Settings           #
######################################
# Alliance Auth validates emails before
# new users can log in.
# It's recommended to use a free service
# like SparkPost or Mailgun to send email.
# https://www.sparkpost.com/docs/integrations/django/
# Set the default from email to something like
# 'noreply@example.com'
#################
EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ''

######################################
# Add any custom settings below here #
######################################
