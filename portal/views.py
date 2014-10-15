from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from eveonline.managers import EveManager

from authentication.managers import AuthServicesInfoManager

# Create your views here.
def index_view(request):
    return render_to_response('public/index.html', None, context_instance=RequestContext(request))


@login_required
def dashboard_view(request):
    render_items = {'characters': EveManager.get_characters_by_owner_id(request.user.id),
                    'authinfo': AuthServicesInfoManager.get_auth_service_info(request.user)}
    return render_to_response('registered/dashboard.html', render_items, context_instance=RequestContext(request))


@login_required
def help_view(request):
    return render_to_response('registered/help.html', None, context_instance=RequestContext(request))
