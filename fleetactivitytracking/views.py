from __future__ import unicode_literals
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.utils import timezone

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.managers import EveManager
from fleetactivitytracking.forms import FatlinkForm
from fleetactivitytracking.models import Fatlink, Fat

from slugify import slugify

from collections import OrderedDict

import string
import random
import datetime

import logging

logger = logging.getLogger(__name__)


class CorpStat(object):
    def __init__(self, corp_id, corp=None, blue=False):
        if corp:
            self.corp = corp
        else:
            self.corp = EveCorporationInfo.objects.get(corporation_id=corp_id)
        self.n_fats = 0
        self.blue = blue

    def avg_fat(self):
        return "%.2f" % (float(self.n_fats) / float(self.corp.member_count))


def first_day_of_next_month(year, month):
    if month == 12:
        return datetime.datetime(year + 1, 1, 1)
    else:
        return datetime.datetime(year, month + 1, 1)


def first_day_of_previous_month(year, month):
    if month == 1:
        return datetime.datetime(year - 1, 12, 1)
    else:
        return datetime.datetime(year, month - 1, 1)


@login_required
def fatlink_view(request):
    # Will show the last 5 or so fatlinks clicked by user.
    # If the user has the right privileges the site will also show the latest fatlinks with the options to add VIPs and
    # manually add players.
    user = request.user
    logger.debug("fatlink_view called by user %s" % request.user)

    latest_fats = Fat.objects.filter(user=user).order_by('-id')[:5]
    if user.has_perm('auth.fleetactivitytracking'):
        latest_links = Fatlink.objects.all().order_by('-id')[:5]
        context = {'user': user, 'fats': latest_fats, 'fatlinks': latest_links}

    else:
        context = {'user': user, 'fats': latest_fats}

    return render(request, 'registered/fatlinkview.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking_statistics')
def fatlink_statistics_view(request, year=datetime.date.today().year, month=datetime.date.today().month):
    year = int(year)
    month = int(month)
    start_of_month = datetime.datetime(year, month, 1)
    start_of_next_month = first_day_of_next_month(year, month)
    start_of_previous_month = first_day_of_previous_month(year, month)

    fatStats = OrderedDict()

    if settings.IS_CORP:
        fatStats[settings.CORP_NAME] = CorpStat(settings.CORP_ID)
    else:
        alliance_corps = EveCorporationInfo.objects.filter(alliance__alliance_id=settings.ALLIANCE_ID)
        for corp in alliance_corps:
            fatStats[corp.corporation_name] = CorpStat(corp.corporation_id, corp=corp)

    fatlinks_in_span = Fatlink.objects.filter(fatdatetime__gte=start_of_month).filter(
        fatdatetime__lt=start_of_next_month)

    for fatlink in fatlinks_in_span:
        fats_in_fatlink = Fat.objects.filter(fatlink=fatlink)
        for fat in fats_in_fatlink:
            fatStats.setdefault(fat.character.corporation_name,
                                CorpStat(fat.character.corporation_id, blue=True)
                                ).n_fats += 1

    fatStatsList = [fatStat for corp_name, fatStat in fatStats.items()]
    fatStatsList.sort(key=lambda stat: stat.corp.corporation_name)
    fatStatsList.sort(key=lambda stat: (stat.n_fats, stat.n_fats / stat.corp.member_count), reverse=True)

    if datetime.datetime.now() > start_of_next_month:
        context = {'fatStats': fatStatsList, 'month': start_of_month.strftime("%B"), 'year': year,
                   'previous_month': start_of_previous_month, 'next_month': start_of_next_month}
    else:
        context = {'fatStats': fatStatsList, 'month': start_of_month.strftime("%B"), 'year': year,
                   'previous_month': start_of_previous_month}

    return render(request, 'registered/fatlinkstatisticsview.html', context=context)


@login_required
def fatlink_personal_statistics_view(request, year=datetime.date.today().year, main_name=None):
    year = int(year)
    logger.debug("Personal statistics view for year %i called by %s" % (year, request.user))

    user = request.user
    logger.debug("fatlink_personal_statistics_view called by user %s" % request.user)

    personal_fats = Fat.objects.filter(user=user).order_by('id')

    monthlystats = [0 for month in range(1, 13)]

    for fat in personal_fats:
        fatdate = fat.fatlink.fatdatetime
        if fatdate.year == year:
            monthlystats[fatdate.month - 1] += 1

    monthlystats = [(i + 1, datetime.date(year, i + 1, 1).strftime("%h"), monthlystats[i]) for i in range(12)]

    if datetime.datetime.now() > datetime.datetime(year + 1, 1, 1):
        context = {'user': user, 'monthlystats': monthlystats, 'year': year, 'previous_year': year - 1,
                   'next_year': year + 1}
    else:
        context = {'user': user, 'monthlystats': monthlystats, 'year': year, 'previous_year': year - 1}

    return render(request, 'registered/fatlinkpersonalstatisticsview.html', context=context)


@login_required
def fatlink_monthly_personal_statistics_view(request, year, month, char_id=None):
    year = int(year)
    month = int(month)
    start_of_month = datetime.datetime(year, month, 1)
    start_of_next_month = first_day_of_next_month(year, month)
    start_of_previous_month = first_day_of_previous_month(year, month)

    if request.user.has_perm('auth.fleetactivitytracking_statistics') and char_id:
        user = EveCharacter.objects.get(character_id=char_id).user
    else:
        user = request.user
    logger.debug("Personal monthly statistics view for user %s called by %s" % (user, request.user))

    personal_fats = Fat.objects.filter(user=user).filter(fatlink__fatdatetime__gte=start_of_month).filter(
        fatlink__fatdatetime__lt=start_of_next_month)

    ship_statistics = dict()
    n_fats = 0
    for fat in personal_fats:
        ship_statistics[fat.shiptype] = ship_statistics.setdefault(fat.shiptype, 0) + 1
        n_fats += 1
    context = {'user': user, 'shipStats': sorted(ship_statistics.items()), 'month': start_of_month.strftime("%h"),
               'year': year, 'n_fats': n_fats, 'char_id': char_id, 'previous_month': start_of_previous_month,
               'next_month': start_of_next_month}

    created_fats = Fatlink.objects.filter(creator=user).filter(fatdatetime__gte=start_of_month).filter(
        fatdatetime__lt=start_of_next_month)
    context["created_fats"] = created_fats
    context["n_created_fats"] = len(created_fats)

    return render(request, 'registered/fatlinkpersonalmonthlystatisticsview.html', context=context)


@login_required
def click_fatlink_view(request, hash, fatname):
    # Take IG-header data and register the fatlink if not existing already.
    # use obj, created = Fat.objects.get_or_create()
    # onload="CCPEVE.requestTrust('http://www.mywebsite.com')"

    if 'HTTP_EVE_TRUSTED' in request.META and request.META['HTTP_EVE_TRUSTED'] == "Yes":
        # Retrieve the latest fatlink using the hash.
        try:
            fatlink = Fatlink.objects.filter(hash=hash)[0]

            if (timezone.now() - fatlink.fatdatetime) < datetime.timedelta(seconds=(fatlink.duration * 60)):

                character = EveManager.get_character_by_id(request.META['HTTP_EVE_CHARID'])

                if character:
                    fat = Fat()
                    fat.system = request.META['HTTP_EVE_SOLARSYSTEMNAME']
                    if 'HTTP_EVE_STATIONNAME' in request.META:
                        fat.station = request.META['HTTP_EVE_STATIONNAME']
                    else:
                        fat.station = "No Station"
                    fat.shiptype = request.META['HTTP_EVE_SHIPTYPENAME']
                    fat.fatlink = fatlink
                    fat.character = character
                    fat.user = character.user
                    try:
                        fat.full_clean()
                        fat.save()
                        context = {'trusted': True, 'registered': True}
                    except ValidationError as e:
                        messages = []
                        for errorname, message in e.message_dict.items():
                            messages.append(message[0].decode())
                        context = {'trusted': True, 'errormessages': messages}
                else:
                    context = {'character_id': request.META['HTTP_EVE_CHARID'],
                               'character_name': request.META['HTTP_EVE_CHARNAME']}
                    return render(request, 'public/characternotexisting.html', context=context)
            else:
                context = {'trusted': True, 'expired': True}
        except ObjectDoesNotExist:
            context = {'trusted': True}
    else:
        context = {'trusted': False, 'fatname': fatname}
    return render(request, 'public/clickfatlinkview.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking')
def create_fatlink_view(request):
    logger.debug("create_fatlink_view called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Post request to create_fatlink_view by user %s" % request.user)
        form = FatlinkForm(request.POST)
        if 'submit_fat' in request.POST:
            logger.debug("Submitting fleetactivitytracking by user %s" % request.user)
            if form.is_valid():
                fatlink = Fatlink()
                fatlink.name = slugify(form.cleaned_data["fatname"])
                fatlink.fleet = form.cleaned_data["fleet"]
                fatlink.duration = form.cleaned_data["duration"]
                fatlink.fatdatetime = timezone.now()
                fatlink.creator = request.user
                fatlink.hash = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                try:
                    fatlink.full_clean()
                    fatlink.save()
                except ValidationError as e:
                    form = FatlinkForm()
                    messages = []
                    for errorname, message in e.message_dict.items():
                        messages.append(message[0].decode())
                    context = {'form': form, 'errormessages': messages}
                    return render(request, 'registered/fatlinkformatter.html', context=context)
            else:
                form = FatlinkForm()
                context = {'form': form, 'badrequest': True}
                return render(request, 'registered/fatlinkformatter.html', context=context)
            return redirect('auth_fatlink_view')

    else:
        form = FatlinkForm()
        logger.debug("Returning empty form to user %s" % request.user)

    context = {'form': form}

    return render(request, 'registered/fatlinkformatter.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking')
def modify_fatlink_view(request, hash=""):
    logger.debug("modify_fatlink_view called by user %s" % request.user)
    if not hash:
        return redirect('/fat/')

    fatlink = Fatlink.objects.filter(hash=hash)[0]

    if request.GET.get('removechar'):
        character_id = request.GET.get('removechar')
        character = EveCharacter.objects.get(character_id=character_id)
        logger.debug("Removing character %s from fleetactivitytracking  %s" % (character.character_name, fatlink.name))

        Fat.objects.filter(fatlink=fatlink).filter(character=character).delete()

    if request.GET.get('deletefat'):
        logger.debug("Removing fleetactivitytracking  %s" % fatlink.name)
        fatlink.delete()
        return redirect('/fat/')

    registered_fats = Fat.objects.filter(fatlink=fatlink).order_by('character')

    context = {'fatlink': fatlink, 'registered_fats': registered_fats}

    return render(request, 'registered/fatlinkmodify.html', context=context)
