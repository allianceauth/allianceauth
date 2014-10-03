from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
def index(request):
    return render_to_response('public/index.html',None, context_instance=RequestContext(request))

