from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from forms import HRApplicationForm


@login_required
def hr_application_management_view(request):
    context = {}

    return render_to_response('registered/hrapplicationmanagement.html',
                              context, context_instance=RequestContext(request))


@login_required
def hr_application_create_view(request):
    if request.method == 'POST':
        form = HRApplicationForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = HRApplicationForm

    context = {'form': form}
    return render_to_response('registered/hrcreateapplication.html',
                              context, context_instance=RequestContext(request))