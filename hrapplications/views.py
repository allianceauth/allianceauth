from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect

from models import HRApplication
from forms import HRApplicationForm
from eveonline.models import EveCorporationInfo
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo


@login_required
def hr_application_management_view(request):
    personal_app = None
    corp_applications = None

    if request.user.is_superuser:
        corp_applications = HRApplication.objects.all()
    else:
        # Get the corp the member is in
        auth_info = AuthServicesInfo.objects.get(user=request.user)
        if auth_info.main_char_id != "":
            main_char = EveCharacter.objects.get(character_id=auth_info.main_char_id)
            corp = EveCorporationInfo.objects.get(corporation_id=main_char.corporation_id)
            corp_applications = HRApplication.objects.filter(corp=corp)

    if HRApplication.objects.filter(user=request.user).exists():
        personal_app = HRApplication.objects.get(user=request.user)

    context = {'personal_app': personal_app,
               'applications': corp_applications}

    return render_to_response('registered/hrapplicationmanagement.html',
                              context, context_instance=RequestContext(request))


@login_required
def hr_application_create_view(request):
    success = False

    if request.method == 'POST':
        form = HRApplicationForm(request.POST)
        if form.is_valid():
            application = HRApplication()
            application.user = request.user
            application.character_name = form.cleaned_data['character_name']
            application.full_api_id = form.cleaned_data['full_api_id']
            application.full_api_key = form.cleaned_data['full_api_key']
            application.corp = EveCorporationInfo.objects.get(corporation_id=form.cleaned_data['corp'])
            application.is_a_spi = form.cleaned_data['is_a_spi']
            application.about = form.cleaned_data['about']
            application.extra = form.cleaned_data['extra']
            application.save()
            success = True
    else:
        form = HRApplicationForm()

    context = {'form': form, 'success': success}
    return render_to_response('registered/hrcreateapplication.html',
                              context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_view(request):
    if HRApplication.objects.filter(user=request.user).exists():
        application = HRApplication.objects.get(user=request.user)

    context = {'application': application}

    return render_to_response('registered/hrapplicationview.html',
                              context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_removal(request):
    if HRApplication.objects.filter(user=request.user).exists():
        application = HRApplication.objects.get(user=request.user)
        application.delete()

    return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_view(request, app_id):
    if HRApplication.objects.filter(id=app_id).exists():
        application = HRApplication.objects.get(id=app_id)

    context = {'application': application}

    return render_to_response('registered/hrapplicationview.html',
                              context, context_instance=RequestContext(request))


@login_required
@permission_required('auth.human_resources')
def hr_application_remove(request, app_id):
    if HRApplication.objects.filter(id=app_id).exists():
        application = HRApplication.objects.get(id=app_id)
        if application:
            application.delete()

    return HttpResponseRedirect("/hr_application_management/")