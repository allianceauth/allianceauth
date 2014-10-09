from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


# Create your views here.
def index_view(request):
    return render_to_response('public/index.html', None, context_instance=RequestContext(request))


@login_required
def dashboard_view(request):
    return render_to_response('registered/dashboard.html', None, context_instance=RequestContext(request))