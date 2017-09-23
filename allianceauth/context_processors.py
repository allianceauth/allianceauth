from django.conf import settings


def auth_settings(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'SITE_NAME': settings.SITE_NAME,
    }
