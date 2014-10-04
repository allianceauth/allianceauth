from django.conf import settings # import the settings file

def alliance_id(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'ALLIANCE_ID': settings.ALLIANCE_ID}

def alliance_name(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'ALLIANCE_NAME': settings.ALLIANCE_NAME}