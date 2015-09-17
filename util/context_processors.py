from django.conf import settings
from django.utils import timezone


def corp_id(request):
    return {'CORP_ID': settings.CORP_ID}


def corp_name(request):
    return {'CORP_NAME': settings.CORP_NAME}


def jabber_url(request):
    return {'JABBER_URL': settings.JABBER_URL}


def domain_url(request):
    return {'DOMAIN': settings.DOMAIN, 'MUMBLE_URL': settings.MUMBLE_URL,
            'FORUM_URL': settings.FORUM_URL,
            'ENABLE_AUTH_FORUM': settings.ENABLE_AUTH_FORUM,
            'ENABLE_AUTH_JABBER': settings.ENABLE_AUTH_JABBER,
            'ENABLE_AUTH_MUMBLE': settings.ENABLE_AUTH_MUMBLE,
            'ENABLE_AUTH_IPBOARD': settings.ENABLE_AUTH_IPBOARD,
            'ENABLE_AUTH_TEAMSPEAK3': settings.ENABLE_AUTH_TEAMSPEAK3,
            'ENABLE_BLUE_JABBER': settings.ENABLE_BLUE_JABBER,
            'ENABLE_BLUE_FORUM': settings.ENABLE_BLUE_FORUM,
            'ENABLE_BLUE_MUMBLE': settings.ENABLE_BLUE_MUMBLE,
            'ENABLE_BLUE_IPBOARD': settings.ENABLE_BLUE_IPBOARD,
            'ENABLE_BLUE_TEAMSPEAK3': settings.ENABLE_BLUE_TEAMSPEAK3,
            'TEAMSPEAK3_PUBLIC_URL': settings.TEAMSPEAK3_PUBLIC_URL,
            'JACK_KNIFE_URL': settings.JACK_KNIFE_URL,
            'CURRENT_UTC_TIME': timezone.now()}
