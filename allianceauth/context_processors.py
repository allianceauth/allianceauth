from django.conf import settings
from django.utils import timezone


def auth_settings(request):
    return {
        'DOMAIN': settings.DOMAIN,

        'IPS4_URL': getattr(settings, 'IPS4_URL', ''),
        'SMF_URL': getattr(settings, 'SMF_URL', ''),
        'MARKET_URL': getattr(settings, 'MARKET_URL', ''),
        'CURRENT_UTC_TIME': timezone.now(),
        'JABBER_URL': getattr(settings, 'JABBER_URL', ''),
        'SITE_NAME': settings.SITE_NAME,
    }
