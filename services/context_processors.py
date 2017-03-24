from __future__ import unicode_literals
from django.conf import settings
from django.utils import timezone


def auth_settings(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'MUMBLE_URL': settings.MUMBLE_URL,
        'FORUM_URL': settings.PHPBB3_URL,
        'TEAMSPEAK3_PUBLIC_URL': settings.TEAMSPEAK3_PUBLIC_URL,
        'DISCORD_SERVER_ID': settings.DISCORD_GUILD_ID,
        'DISCOURSE_URL': settings.DISCOURSE_URL,
        'IPS4_URL': settings.IPS4_URL,
        'SMF_URL': settings.SMF_URL,
        'MARKET_URL': settings.MARKET_URL,
        'CURRENT_UTC_TIME': timezone.now(),
        'JABBER_URL': settings.JABBER_URL,
        'SITE_NAME': settings.SITE_NAME,
    }
