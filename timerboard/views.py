import datetime

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

from util import check_if_user_has_permission
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from form import TimerForm
from models import Timer


def timer_util_test(user):
    return check_if_user_has_permission(user, 'alliance_member') or check_if_user_has_permission(user, 'blue_member')


@login_required
@user_passes_test(timer_util_test)
def timer_view(request):
    timer_list = Timer.objects.all()
    closest_timer = None
    if timer_list:
        closest_timer = \
        sorted(list(Timer.objects.all()), key=lambda d: abs(datetime.datetime.now() - d.eve_time.replace(tzinfo=None)))[
            0]

    render_items = {'timers': Timer.objects.all(),
                    'closest_timer': closest_timer}

    return render_to_response('registered/timermanagement.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.timer_management')
def add_timer_view(request):
    if request.method == 'POST':
        form = TimerForm(request.POST)

        if form.is_valid():
            # Get character
            auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
            character = EveManager.get_character_by_id(auth_info.main_char_id)
            corporation = EveManager.get_corporation_info_by_id(character.corporation_id)

            # handle valid form
            timer = Timer()
            timer.name = form.cleaned_data['name']
            timer.system = form.cleaned_data['system']
            timer.planet_moon = form.cleaned_data['planet_moon']
            timer.structure = form.cleaned_data['structure']
            timer.fleet_type = form.cleaned_data['fleet_type']
            timer.eve_time = form.cleaned_data['eve_time']
            timer.important = form.cleaned_data['important']
            timer.eve_character = character
            timer.eve_corp = corporation
            timer.user = request.user
            timer.save()
            return HttpResponseRedirect("/timers/")
    else:
        form = TimerForm()

    render_items = {'form': form}

    return render_to_response('registered/addtimer.html', render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.timer_management')
def remove_timer(request, timer_id):
    if Timer.objects.filter(id=timer_id).exists():
        timer = Timer.objects.get(id=timer_id)
        timer.delete()
    return HttpResponseRedirect("/timers/")