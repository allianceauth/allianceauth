from .base import *

# These are required for Django to function properly
ROOT_URLCONF = '{{ project_name }}.urls'
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]
TEMPLATES[0]['DIRS'] += [os.path.join(PROJECT_DIR, 'templates')]
SECRET_KEY = '{{ secret_key }}'

# Change this to change the name of the auth site
SITE_NAME = '{{ project_name }}'

# Change this to enable/disable debug mode
DEBUG = False


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
# Add any custom settings below here #
######################################
