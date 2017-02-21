from __future__ import unicode_literals
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.managers import EveManager
from fleetactivitytracking.forms import FatlinkForm
from fleetactivitytracking.models import Fatlink, Fat

from esi.decorators import token_required

from slugify import slugify

import string
import random
import datetime

import logging

logger = logging.getLogger(__name__)

FATS_PER_PAGE = int(getattr(settings, 'FATS_PER_PAGE', 20))


def get_page(model_list, page_num):
    p = Paginator(model_list, FATS_PER_PAGE)
    try:
        fats = p.page(page_num)
    except PageNotAnInteger:
        fats = p.page(1)
    except EmptyPage:
        fats = p.page(p.num_pages)
    return fats


class CorpStat(object):
    def __init__(self, corp_id, start_of_month, start_of_next_month, corp=None):
        if corp:
            self.corp = corp
        else:
            self.corp = EveCorporationInfo.objects.get(corporation_id=corp_id)
        self.n_fats = Fat.objects.filter(character__corporation_id=self.corp.corporation_id).filter(
            fatlink__fatdatetime__gte=start_of_month).filter(fatlink__fatdatetime__lte=start_of_next_month).count()
        self.blue = self.corp.is_blue

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

    return render(request, 'fleetactivitytracking/fatlinkview.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking_statistics')
def fatlink_statistics_view(request, year=datetime.date.today().year, month=datetime.date.today().month):
    year = int(year)
    month = int(month)
    start_of_month = datetime.datetime(year, month, 1)
    start_of_next_month = first_day_of_next_month(year, month)
    start_of_previous_month = first_day_of_previous_month(year, month)

    fat_stats = {}

    # get FAT stats for member corps
    for corp_id in settings.STR_CORP_IDS:
        fat_stats[corp_id] = CorpStat(corp_id, start_of_month, start_of_next_month)
    for alliance_id in settings.STR_ALLIANCE_IDS:
        alliance_corps = EveCorporationInfo.objects.filter(alliance__alliance_id=alliance_id)
        for corp in alliance_corps:
            fat_stats[corp.corporation_id] = CorpStat(corp.corporation_id, start_of_month, start_of_next_month)

    # get FAT stats for corps not in alliance
    fats_in_span = Fat.objects.filter(fatlink__fatdatetime__gte=start_of_month).filter(
        fatlink__fatdatetime__lt=start_of_next_month).exclude(character__corporation_id__in=fat_stats)

    for fat in fats_in_span:
        if fat.character.corporation_id not in fat_stats:
            fat_stats[fat.character.corporation_id] = CorpStat(fat.character.corporation_id, start_of_month,
                                                               start_of_next_month)

    # collect and sort stats
    stat_list = [fat_stats[x] for x in fat_stats]
    stat_list.sort(key=lambda stat: stat.corp.corporation_name)
    stat_list.sort(key=lambda stat: (stat.n_fats, stat.n_fats / stat.corp.member_count), reverse=True)

    if datetime.datetime.now() > start_of_next_month:
        context = {'fatStats': stat_list, 'month': start_of_month.strftime("%B"), 'year': year,
                   'previous_month': start_of_previous_month, 'next_month': start_of_next_month}
    else:
        context = {'fatStats': stat_list, 'month': start_of_month.strftime("%B"), 'year': year,
                   'previous_month': start_of_previous_month}

    return render(request, 'fleetactivitytracking/fatlinkstatisticsview.html', context=context)


@login_required
def fatlink_personal_statistics_view(request, year=datetime.date.today().year):
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

    return render(request, 'fleetactivitytracking/fatlinkpersonalstatisticsview.html', context=context)


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

    return render(request, 'fleetactivitytracking/fatlinkpersonalmonthlystatisticsview.html', context=context)


@login_required
@token_required(
    scopes=['esi-location.read_location.v1', 'esi-location.read_ship_type.v1', 'esi-universe.read_structures.v1'])
def click_fatlink_view(request, token, hash, fatname):
    try:
        fatlink = Fatlink.objects.filter(hash=hash)[0]

        if (timezone.now() - fatlink.fatdatetime) < datetime.timedelta(seconds=(fatlink.duration * 60)):

            character = EveManager.get_character_by_id(token.character_id)

            if character:
                # get data
                c = token.get_esi_client(Location='v1', Universe='v2')
                location = c.Location.get_characters_character_id_location(character_id=token.character_id).result()
                ship = c.Location.get_characters_character_id_ship(character_id=token.character_id).result()
                location['solar_system_name'] = \
                    c.Universe.get_universe_systems_system_id(system_id=location['solar_system_id']).result()[
                        'name']
                if location['structure_id']:
                    location['station_name'] = \
                        c.Universe.get_universe_structures_structure_id(structure_id=location['structure_id']).result()[
                            'name']
                elif location['station_id']:
                    location['station_name'] = \
                        c.Universe.get_universe_stations_station_id(station_id=location['station_id']).result()['name']
                else:
                    location['station_name'] = "No Station"
                ship['ship_type_name'] = EveManager.get_itemtype(ship['ship_type_id']).name

                fat = Fat()
                fat.system = location['solar_system_name']
                fat.station = location['station_name']
                fat.shiptype = ship['ship_type_name']
                fat.fatlink = fatlink
                fat.character = character
                fat.user = character.user
                try:
                    fat.full_clean()
                    fat.save()
                    messages.success(request, _('Fleet participation registered.'))
                except ValidationError as e:
                    err_messages = []
                    for errorname, message in e.message_dict.items():
                        err_messages.append(message[0].decode())
                    messages.error(request, ' '.join(err_messages))
            else:
                context = {'character_id': token.character_id,
                           'character_name': token.character_name}
                return render(request, 'fleetactivitytracking/characternotexisting.html', context=context)
        else:
            messages.error(request, _('FAT link has expired.'))
    except (ObjectDoesNotExist, KeyError):
        logger.exception("Failed to process FAT link.")
        messages.error(request, _('Invalid FAT link.'))
    return redirect('auth_fatlink_view')


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
                    return render(request, 'fleetactivitytracking/fatlinkformatter.html', context=context)
            else:
                form = FatlinkForm()
                context = {'form': form, 'badrequest': True}
                return render(request, 'registered/fatlinkformatter.html', context=context)
            return redirect('auth_fatlink_view')

    else:
        form = FatlinkForm()
        logger.debug("Returning empty form to user %s" % request.user)

    context = {'form': form}

    return render(request, 'fleetactivitytracking/fatlinkformatter.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking')
def modify_fatlink_view(request, hash=""):
    logger.debug("modify_fatlink_view called by user %s" % request.user)
    if not hash:
        return redirect('auth_fatlink_view')

    fatlink = Fatlink.objects.filter(hash=hash)[0]

    if request.GET.get('removechar', None):
        character_id = request.GET.get('removechar')
        character = EveCharacter.objects.get(character_id=character_id)
        logger.debug("Removing character %s from fleetactivitytracking  %s" % (character.character_name, fatlink.name))

        Fat.objects.filter(fatlink=fatlink).filter(character=character).delete()

    if request.GET.get('deletefat', None):
        logger.debug("Removing fleetactivitytracking  %s" % fatlink.name)
        fatlink.delete()
        return redirect('auth_fatlink_view')

    registered_fats = Fat.objects.filter(fatlink=fatlink).order_by('character__character_name')

    fat_page = get_page(registered_fats, request.GET.get('page', 1))

    context = {'fatlink': fatlink, 'registered_fats': fat_page}

    return render(request, 'fleetactivitytracking/fatlinkmodify.html', context=context)
