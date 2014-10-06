from django.conf import settings


def alliance_id(request):
    return {'ALLIANCE_ID': settings.ALLIANCE_ID}


def alliance_name(request):
    return {'ALLIANCE_NAME': settings.ALLIANCE_NAME}