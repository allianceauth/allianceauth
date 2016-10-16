from __future__ import unicode_literals
from django.conf import settings
from django.utils import timezone


def auth_settings(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'MUMBLE_URL': settings.MUMBLE_URL,
        'FORUM_URL': settings.FORUM_URL,
        'TEAMSPEAK3_PUBLIC_URL': settings.TEAMSPEAK3_PUBLIC_URL,
        'JACK_KNIFE_URL': settings.JACK_KNIFE_URL,
        'DISCORD_SERVER_ID': settings.DISCORD_GUILD_ID,
        'KILLBOARD_URL': settings.KILLBOARD_URL,
        'DISCOURSE_URL': settings.DISCOURSE_URL,
        'IPS4_URL': settings.IPS4_URL,
        'SMF_URL': settings.SMF_URL,
        'MARKET_URL': settings.MARKET_URL,
        'EXTERNAL_MEDIA_URL': settings.EXTERNAL_MEDIA_URL,
        'CURRENT_UTC_TIME': timezone.now(),
        'BLUE_API_MASK': settings.BLUE_API_MASK,
        'BLUE_API_ACCOUNT': settings.BLUE_API_ACCOUNT,
        'MEMBER_API_MASK': settings.MEMBER_API_MASK,
        'MEMBER_API_ACCOUNT': settings.MEMBER_API_ACCOUNT,
        'JABBER_URL': settings.JABBER_URL,
        'ALLIANCE_NAME': settings.ALLIANCE_NAME,
        'ALLIANCE_ID': settings.ALLIANCE_ID,
        'CORP_NAME': settings.CORP_NAME,
        'CORP_ID': settings.CORP_ID,
        'IS_CORP': settings.IS_CORP,
    }