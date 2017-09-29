from django.conf import settings


def auth_settings(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
    }
