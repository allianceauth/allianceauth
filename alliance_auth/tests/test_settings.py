"""
Alliance Auth Test Suite Django settings.
"""

import os

from django.contrib import messages

import alliance_auth

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    #'--with-coverage',
    #'--cover-package=',
    #'--exe',  # If your tests need this to be found/run, check they py files are not chmodded +x
]

# Celery configuration
CELERY_ALWAYS_EAGER = True  # Forces celery to run locally for testing

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(alliance_auth.__file__)))

SECRET_KEY = 'testing only'

DEBUG = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_celery_beat',
    'bootstrapform',
    'authentication',
    'services',
    'eveonline',
    'groupmanagement',
    'hrapplications',
    'timerboard',
    'srp',
    'optimer',
    'corputils',
    'fleetactivitytracking',
    'fleetup',
    'notifications',
    'esi',
    'permissions_tool',
    'geelweb.django.navhelper',
    'bootstrap_pagination',
    'services.modules.mumble',
    'services.modules.discord',
    'services.modules.discourse',
    'services.modules.ipboard',
    'services.modules.ips4',
    'services.modules.market',
    'services.modules.openfire',
    'services.modules.seat',
    'services.modules.smf',
    'services.modules.phpbb3',
    'services.modules.xenforo',
    'services.modules.teamspeak3',
    'django_nose',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'alliance_auth.urls'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
    ('de', ugettext('German')),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'customization/templates'),
            os.path.join(BASE_DIR, 'stock/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'services.context_processors.auth_settings',
                'notifications.context_processors.user_notification_count',
                'authentication.context_processors.states',
                'authentication.context_processors.membership_state',
                'groupmanagement.context_processors.can_manage_groups',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'alliance_auth',
        'USER': os.environ.get('AA_DB_DEFAULT_USER', None),
        'PASSWORD': os.environ.get('AA_DB_DEFAULT_PASSWORD', None),
        'HOST': os.environ.get('AA_DB_DEFAULT_HOST', None)
    },
}

LOGIN_URL = 'auth_login_user'

SUPERUSER_STATE_BYPASS = 'True' == os.environ.get('AA_SUPERUSER_STATE_BYPASS', 'True')

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = os.environ.get('AA_LANGUAGE_CODE', 'en')

TIME_ZONE = os.environ.get('AA_TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "customization/static"),
    os.path.join(BASE_DIR, "stock/static"),
)

# Bootstrap messaging css workaround
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#####################################################
##
## Auth configuration starts here
##
#####################################################

###########################
# ALLIANCE / CORP TOGGLE
###########################
# Specifies to run membership checks against corp or alliance
# Set to FALSE for alliance
# Set to TRUE for corp
###########################
IS_CORP = 'True' == os.environ.get('AA_IS_CORP', 'True')

#################
# EMAIL SETTINGS
#################
# DOMAIN - The alliance auth domain_url
# EMAIL_HOST - SMTP Server URL
# EMAIL_PORT - SMTP Server PORT
# EMAIL_HOST_USER - Email Username (for gmail, the entire address)
# EMAIL_HOST_PASSWORD - Email Password
# EMAIL_USE_TLS - Set to use TLS encryption
#################
DOMAIN = os.environ.get('AA_DOMAIN', 'https://example.com')
EMAIL_HOST = os.environ.get('AA_EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('AA_EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('AA_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('AA_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = 'True' == os.environ.get('AA_EMAIL_USE_TLS', 'True')

####################
# Front Page Links
####################
# KILLBOARD_URL - URL for your killboard. Blank to hide link
# MEDIA_URL - URL for your media page (youtube etc). Blank to hide link
# FORUM_URL - URL for your forums. Blank to hide link
# SITE_NAME - Name of the auth site.
####################
KILLBOARD_URL = os.environ.get('AA_KILLBOARD_URL', '')
EXTERNAL_MEDIA_URL = os.environ.get('AA_EXTERNAL_MEDIA_URL', '')
FORUM_URL = os.environ.get('AA_FORUM_URL', '')
SITE_NAME = os.environ.get('AA_SITE_NAME', 'Test Alliance Auth')

###################
# SSO Settings
###################
# Optional SSO.
# Get client ID and client secret from registering an app at
# https://developers.eveonline.com/
# Callback URL should be http://mydomain.com/sso/callback
# Leave callback blank to hide SSO button on login page
###################
ESI_SSO_CLIENT_ID = os.environ.get('AA_ESI_SSO_CLIENT_ID', '')
ESI_SSO_CLIENT_SECRET = os.environ.get('AA_ESI_SSO_CLIENT_SECRET', '')
ESI_SSO_CALLBACK_URL = os.environ.get('AA_ESI_SSO_CALLBACK_URL', '')

#########################
# Default Group Settings
#########################
# DEFAULT_AUTH_GROUP - Default group members are put in
# DEFAULT_BLUE_GROUP - Default group for blue members
# MEMBER_CORP_GROUPS - Assign members to a group representing their main corp
# BLUE_CORP_GROUPS - Assign blues to a group representing their main corp
#########################
DEFAULT_AUTH_GROUP = os.environ.get('AA_DEFAULT_ALLIANCE_GROUP', 'Member')
DEFAULT_BLUE_GROUP = os.environ.get('AA_DEFAULT_BLUE_GROUP', 'Blue')
MEMBER_CORP_GROUPS = 'True' == os.environ.get('AA_MEMBER_CORP_GROUPS', 'True')
MEMBER_ALLIANCE_GROUPS = 'True' == os.environ.get('AA_MEMBER_ALLIANCE_GROUPS', 'False')
BLUE_CORP_GROUPS = 'True' == os.environ.get('AA_BLUE_CORP_GROUPS', 'False')
BLUE_ALLIANCE_GROUPS = 'True' == os.environ.get('AA_BLUE_ALLIANCE_GROUPS', 'False')

#########################
# Corp Configuration
#########################
# If running in alliance mode, the following should be for the executor corp#
# CORP_ID - Set this to your corp ID (get this from https://zkillboard.com/corporation/#######)
# CORP_NAME - Set this to your Corporation Name
# CORP_API_ID - Set this to the api id for the corp API key
# CORP_API_VCODE - Set this to the api vcode for the corp API key
########################
CORP_ID = os.environ.get('AA_CORP_ID', '1234')
CORP_NAME = os.environ.get('AA_CORP_NAME', 'Alliance Auth Test Corp')
CORP_API_ID = os.environ.get('AA_CORP_API_ID', '')
CORP_API_VCODE = os.environ.get('AA_CORP_API_VCODE', '')

#########################
# Alliance Configuration
#########################
# ALLIANCE_ID - Set this to your Alliance ID (get this from https://zkillboard.com/alliance/#######)
# ALLIANCE_NAME - Set this to your Alliance Name
########################
ALLIANCE_ID = os.environ.get('AA_ALLIANCE_ID', '12345')
ALLIANCE_NAME = os.environ.get('AA_ALLIANCE_NAME', 'Alliance Auth Test Alliance')

########################
# API Configuration
########################
# MEMBER_API_MASK - Numeric value of minimum API mask required for members
# MEMBER_API_ACCOUNT - Require API to be for Account and not character restricted
# BLUE_API_MASK - Numeric value of minimum API mask required for blues
# BLUE_API_ACCOUNT - Require API to be for Account and not character restricted
# REJECT_OLD_APIS - Require each submitted API be newer than the latest submitted API
# REJECT_OLD_APIS_MARGIN - Margin from latest submitted API ID within which a newly submitted API is still accepted
# API_SSO_VALIDATION - Require users to prove ownership of newly entered API keys via SSO
#                      Requires SSO to be configured.
#######################
MEMBER_API_MASK = os.environ.get('AA_MEMBER_API_MASK', 268435455)
MEMBER_API_ACCOUNT = 'True' == os.environ.get('AA_MEMBER_API_ACCOUNT', 'True')
BLUE_API_MASK = os.environ.get('AA_BLUE_API_MASK', 8388608)
BLUE_API_ACCOUNT = 'True' == os.environ.get('AA_BLUE_API_ACCOUNT', 'True')
REJECT_OLD_APIS = 'True' == os.environ.get('AA_REJECT_OLD_APIS', 'False')
REJECT_OLD_APIS_MARGIN = os.environ.get('AA_REJECT_OLD_APIS_MARGIN', 50)
API_SSO_VALIDATION = 'True' == os.environ.get('AA_API_SSO_VALIDATION', 'False')

#######################
# EVE Provider Settings
#######################
# EVEONLINE_CHARACTER_PROVIDER - Name of default data source for getting eve character data
# EVEONLINE_CORP_PROVIDER - Name of default data source for getting eve corporation data
# EVEONLINE_ALLIANCE_PROVIDER - Name of default data source for getting eve alliance data
# EVEONLINE_ITEMTYPE_PROVIDER - Name of default data source for getting eve item type data
#
# Available sources are 'esi' and 'xml'. Leaving blank results in the default 'esi' being used.
#######################
EVEONLINE_CHARACTER_PROVIDER = os.environ.get('AA_EVEONLINE_CHARACTER_PROVIDER', 'xml')
EVEONLINE_CORP_PROVIDER = os.environ.get('AA_EVEONLINE_CORP_PROVIDER', 'xml')
EVEONLINE_ALLIANCE_PROVIDER = os.environ.get('AA_EVEONLINE_ALLIANCE_PROVIDER', 'xml')
EVEONLINE_ITEMTYPE_PROVIDER = os.environ.get('AA_EVEONLINE_ITEMTYPE_PROVIDER', 'xml')

#####################
# Alliance Market
#####################
MARKET_URL = os.environ.get('AA_MARKET_URL', 'http://yourdomain.com/market')

#####################
# HR Configuration
#####################
# JACK_KNIFE_URL - Url for the audit page of API Jack knife
#                  Should seriously replace with your own.
#####################
JACK_KNIFE_URL = os.environ.get('AA_JACK_KNIFE_URL', 'http://example.com/eveapi/audit.php')

#####################
# Forum Configuration
#####################
# IPBOARD_ENDPOINT - Api endpoint if using ipboard
# IPBOARD_APIKEY - Api key to interact with ipboard
# IPBOARD_APIMODULE - Module for alliance auth *leave alone*
#####################
IPBOARD_ENDPOINT = os.environ.get('AA_IPBOARD_ENDPOINT', 'example.com/interface/board/index.php')
IPBOARD_APIKEY = os.environ.get('AA_IPBOARD_APIKEY', 'somekeyhere')
IPBOARD_APIMODULE = 'aa'

########################
# XenForo Configuration
########################
XENFORO_ENDPOINT = os.environ.get('AA_XENFORO_ENDPOINT', 'example.com/api.php')
XENFORO_DEFAULT_GROUP = os.environ.get('AA_XENFORO_DEFAULT_GROUP', 0)
XENFORO_APIKEY   = os.environ.get('AA_XENFORO_APIKEY', 'yourapikey')
#####################

######################
# Jabber Configuration
######################
# JABBER_URL - Jabber address url
# JABBER_PORT - Jabber service portal
# JABBER_SERVER - Jabber server url
# OPENFIRE_ADDRESS - Address of the openfire admin console including port
#                    Please use http with 9090 or https with 9091
# OPENFIRE_SECRET_KEY - Openfire REST API secret key
# BROADCAST_USER - Broadcast user JID
# BROADCAST_USER_PASSWORD - Broadcast user password
######################
JABBER_URL = os.environ.get('AA_JABBER_URL', "example.com")
JABBER_PORT = int(os.environ.get('AA_JABBER_PORT', '5223'))
JABBER_SERVER = os.environ.get('AA_JABBER_SERVER', "example.com")
OPENFIRE_ADDRESS = os.environ.get('AA_OPENFIRE_ADDRESS', "http://example.com:9090")
OPENFIRE_SECRET_KEY = os.environ.get('AA_OPENFIRE_SECRET_KEY', "somekey")
BROADCAST_USER = os.environ.get('AA_BROADCAST_USER', "broadcast@") + JABBER_URL
BROADCAST_USER_PASSWORD = os.environ.get('AA_BROADCAST_USER_PASSWORD', "somepassword")
BROADCAST_SERVICE_NAME = os.environ.get('AA_BROADCAST_SERVICE_NAME', "broadcast")

######################################
# Mumble Configuration
######################################
# MUMBLE_URL - Mumble server url
# MUMBLE_SERVER_ID - Mumble server id
######################################
MUMBLE_URL = os.environ.get('AA_MUMBLE_URL', "example.com")
MUMBLE_SERVER_ID = int(os.environ.get('AA_MUMBLE_SERVER_ID', '1'))

######################################
# PHPBB3 Configuration
######################################

######################################
# Teamspeak3 Configuration
######################################
# TEAMSPEAK3_SERVER_IP - Teamspeak3 server ip
# TEAMSPEAK3_SERVER_PORT - Teamspeak3 server port
# TEAMSPEAK3_SERVERQUERY_USER - Teamspeak3 serverquery username
# TEAMSPEAK3_SERVERQUERY_PASSWORD - Teamspeak3 serverquery password
# TEAMSPEAK3_VIRTUAL_SERVER - Virtual server id
# TEAMSPEAK3_AUTHED_GROUP_ID - Default authed group id
# TEAMSPEAK3_PUBLIC_URL - teamspeak3 public url used for link creation
######################################
TEAMSPEAK3_SERVER_IP = os.environ.get('AA_TEAMSPEAK3_SERVER_IP', '127.0.0.1')
TEAMSPEAK3_SERVER_PORT = int(os.environ.get('AA_TEAMSPEAK3_SERVER_PORT', '10011'))
TEAMSPEAK3_SERVERQUERY_USER = os.environ.get('AA_TEAMSPEAK3_SERVERQUERY_USER', 'serveradmin')
TEAMSPEAK3_SERVERQUERY_PASSWORD = os.environ.get('AA_TEAMSPEAK3_SERVERQUERY_PASSWORD', 'passwordhere')
TEAMSPEAK3_VIRTUAL_SERVER = int(os.environ.get('AA_TEAMSPEAK3_VIRTUAL_SERVER', '1'))
TEAMSPEAK3_PUBLIC_URL = os.environ.get('AA_TEAMSPEAK3_PUBLIC_URL', 'example.com')

######################################
# Discord Configuration
######################################
# DISCORD_GUILD_ID - ID of the guild to manage
# DISCORD_BOT_TOKEN - oauth token of the app bot user
# DISCORD_INVITE_CODE - invite code to the server
# DISCORD_APP_ID - oauth app client ID
# DISCORD_APP_SECRET - oauth app secret
# DISCORD_CALLBACK_URL - oauth callback url
# DISCORD_SYNC_NAMES - enable to force discord nicknames to be set to eve char name (bot needs Manage Nicknames permission)
######################################
DISCORD_GUILD_ID = os.environ.get('AA_DISCORD_GUILD_ID', '0118999')
DISCORD_BOT_TOKEN = os.environ.get('AA_DISCORD_BOT_TOKEN', 'bottoken')
DISCORD_INVITE_CODE = os.environ.get('AA_DISCORD_INVITE_CODE', 'invitecode')
DISCORD_APP_ID = os.environ.get('AA_DISCORD_APP_ID', 'appid')
DISCORD_APP_SECRET = os.environ.get('AA_DISCORD_APP_SECRET', 'secret')
DISCORD_CALLBACK_URL = os.environ.get('AA_DISCORD_CALLBACK_URL', 'http://example.com/discord/callback')
DISCORD_SYNC_NAMES = 'True' == os.environ.get('AA_DISCORD_SYNC_NAMES', 'False')

######################################
# Discourse Configuration
######################################
# DISCOURSE_URL - Web address of the forums (no trailing slash)
# DISCOURSE_API_USERNAME - API account username
# DISCOURSE_API_KEY - API Key
# DISCOURSE_SSO_SECRET - SSO secret key
######################################
DISCOURSE_URL = os.environ.get('AA_DISCOURSE_URL', 'https://example.com')
DISCOURSE_API_USERNAME = os.environ.get('AA_DISCOURSE_API_USERNAME', '')
DISCOURSE_API_KEY = os.environ.get('AA_DISCOURSE_API_KEY', '')
DISCOURSE_SSO_SECRET = 'd836444a9e4084d5b224a60c208dce14'
# Example secret from https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045

#####################################
# IPS4 Configuration
#####################################
# IPS4_URL - base url of the IPS4 install (no trailing slash)
# IPS4_API_KEY - API key provided by IPS4
#####################################
IPS4_URL = os.environ.get('AA_IPS4_URL', 'http://example.com/ips4')
IPS4_API_KEY = os.environ.get('AA_IPS4_API_KEY', '')

#####################################
# SEAT Configuration
#####################################
# SEAT_URL - base url of the seat install (no trailing slash)
# SEAT_XTOKEN - API key X-Token provided by SeAT
#####################################
SEAT_URL = os.environ.get('AA_SEAT_URL', 'http://example.com/seat')
SEAT_XTOKEN = os.environ.get('AA_SEAT_XTOKEN', 'tokentokentoken')

######################################
# SMF Configuration
######################################
SMF_URL = os.environ.get('AA_SMF_URL', '')

######################################
# Fleet-Up Configuration
######################################
# FLEETUP_APP_KEY - The app key from http://fleet-up.com/Api/MyApps
# FLEETUP_USER_ID - The user id from http://fleet-up.com/Api/MyKeys
# FLEETUP_API_ID - The API id from http://fleet-up.com/Api/MyKeys
# FLEETUP_GROUP_ID - The id of the group you want to pull data from, see http://fleet-up.com/Api/Endpoints#groups_mygroupmemberships
######################################
FLEETUP_APP_KEY = os.environ.get('AA_FLEETUP_APP_KEY', '')
FLEETUP_USER_ID = os.environ.get('AA_FLEETUP_USER_ID', '')
FLEETUP_API_ID = os.environ.get('AA_FLEETUP_API_ID', '')
FLEETUP_GROUP_ID = os.environ.get('AA_FLEETUP_GROUP_ID', '')

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',        # edit this line to change logging level to console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'notifications': {           # creates notifications for users with logging_notifications permission
            'level': 'ERROR',        # edit this line to change logging level to notifications
            'class': 'notifications.handlers.NotificationHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'authentication': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'celerytask': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'eveonline': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'groupmanagement': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'hrapplications': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'portal': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'registration': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'srp': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'timerboard': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'sigtracker': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'optimer': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'corputils': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'fleetactivitytracking': {
            'handlers': ['console', 'notifications'],
            'level': 'ERROR',
        },
        'util': {
            'handlers': ['console', 'notifications'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console', 'notifications'],
            'level': 'ERROR',
        },
    }
}

LOGGING = None  # Comment out to enable logging for debugging
