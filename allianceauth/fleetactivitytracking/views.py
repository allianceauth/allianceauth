import datetime
import logging
import os

from allianceauth.authentication.models import CharacterOwnership
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from esi.decorators import token_required
from allianceauth.eveonline.providers import provider
from .forms import FatlinkForm
from .models import Fatlink, Fat
from django.utils.crypto import get_random_string

from allianceauth.eveonline.models import EveAllianceInfo
from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.models import EveCorporationInfo

SWAGGER_SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')
"""
Swagger spec operations:

get_characters_character_id_location
get_characters_character_id_ship
get_universe_systems_system_id
get_universe_stations_station_id
get_universe_structures_structure_id
"""


logger = logging.getLogger(__name__)


class CorpStat(object):
    def __init__(self, corp_id, start_of_month, start_of_next_month, corp=None):
        if corp:
            self.corp = corp
        else:
            self.corp = EveCorporationInfo.objects.get(corporation_id=corp_id)
        self.n_fats = Fat.objects.filter(character__corporation_id=self.corp.corporation_id).filter(
            fatlink__fatdatetime__gte=start_of_month).filter(fatlink__fatdatetime__lte=start_of_next_month).count()

    @property
    def avg_fat(self):
        try:
            return "%.2f" % (float(self.n_fats) / float(self.corp.member_count))
        except ZeroDivisionError:
            return "%.2f" % 0


class MemberStat(object):
    def __init__(self, member, start_of_month, start_of_next_month, mainchid=None):
        if mainchid:
            self.mainchid = mainchid
        else:
            self.mainchid = member.profile.main_character.character_id if member.profile.main_character else None
        self.mainchar = EveCharacter.objects.get(character_id=self.mainchid)
        nchars = 0
        for alliance in EveAllianceInfo.objects.all():
            nchars += EveCharacter.objects.filter(character_ownership__user=member).filter(alliance_id=alliance.alliance_id).count()
        self.n_chars = nchars
        self.n_fats = Fat.objects.filter(user_id=member.pk).filter(
            fatlink__fatdatetime__gte=start_of_month).filter(fatlink__fatdatetime__lte=start_of_next_month).count()

    @property
    def avg_fat(self):
        try:
            return "%.2f" % (float(self.n_fats) / float(self.n_chars))
        except ZeroDivisionError:
            return "%.2f" % 0


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

    latest_fats = Fat.objects.select_related('character', 'fatlink').filter(user=user).order_by('-id')[:5]
    if user.has_perm('auth.fleetactivitytracking'):
        latest_links = Fatlink.objects.select_related('creator').all().order_by('-id')[:5]
        context = {'user': user, 'fats': latest_fats, 'fatlinks': latest_links}

    else:
        context = {'user': user, 'fats': latest_fats}

    return render(request, 'fleetactivitytracking/fatlinkview.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking_statistics')
def fatlink_statistics_corp_view(request, corpid, year=None, month=None):
    if year is None:
        year = datetime.date.today().year
    if month is None:
        month = datetime.date.today().month

    year = int(year)
    month = int(month)
    start_of_month = datetime.datetime(year, month, 1)
    start_of_next_month = first_day_of_next_month(year, month)
    start_of_previous_month = first_day_of_previous_month(year, month)
    fat_stats = {}
    corp_members = CharacterOwnership.objects.filter(character__corporation_id=corpid).values('user_id').distinct()

    for member in corp_members:
        try:
            fat_stats[member['user_id']] = MemberStat(User.objects.get(pk=member['user_id']), start_of_month, start_of_next_month)
        except ObjectDoesNotExist:
            continue

    # collect and sort stats
    stat_list = [fat_stats[x] for x in fat_stats]
    stat_list.sort(key=lambda stat: stat.mainchar.character_name)
    stat_list.sort(key=lambda stat: (stat.n_fats, stat.avg_fat), reverse=True)

    context = {'fatStats': stat_list, 'month': start_of_month.strftime("%B"), 'year': year,
           'previous_month': start_of_previous_month, 'corpid': corpid}
    if datetime.datetime.now() > start_of_next_month:
        context.update({'next_month': start_of_next_month})

    return render(request, 'fleetactivitytracking/fatlinkstatisticscorpview.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking_statistics')
def fatlink_statistics_view(request, year=datetime.date.today().year, month=datetime.date.today().month):
    year = int(year)
    month = int(month)
    start_of_month = datetime.datetime(year, month, 1)
    start_of_next_month = first_day_of_next_month(year, month)
    start_of_previous_month = first_day_of_previous_month(year, month)

    fat_stats = {}

    for corp in EveCorporationInfo.objects.all():
        fat_stats[corp.corporation_id] = CorpStat(corp.corporation_id, start_of_month, start_of_next_month)

    # get FAT stats for corps without models
    fats_in_span = Fat.objects.filter(fatlink__fatdatetime__gte=start_of_month).filter(
        fatlink__fatdatetime__lt=start_of_next_month).exclude(character__corporation_id__in=fat_stats)

    for fat in fats_in_span.exclude(character__corporation_id__in=fat_stats):
        if EveCorporationInfo.objects.filter(corporation_id=fat.character.corporation_id).exists():
            fat_stats[fat.character.corporation_id] = CorpStat(fat.character.corporation_id, start_of_month,
                                                               start_of_next_month)

    # collect and sort stats
    stat_list = [fat_stats[x] for x in fat_stats]
    stat_list.sort(key=lambda stat: stat.corp.corporation_name)
    stat_list.sort(key=lambda stat: (stat.n_fats, stat.avg_fat), reverse=True)

    context = {'fatStats': stat_list, 'month': start_of_month.strftime("%B"), 'year': year,
           'previous_month': start_of_previous_month}
    if datetime.datetime.now() > start_of_next_month:
        context.update({'next_month': start_of_next_month})

    return render(request, 'fleetactivitytracking/fatlinkstatisticsview.html', context=context)


@login_required
def fatlink_personal_statistics_view(request, year=datetime.date.today().year):
    year = int(year)
    logger.debug("Personal statistics view for year %i called by %s" % (year, request.user))

    user = request.user
    logger.debug("fatlink_personal_statistics_view called by user %s" % request.user)

    personal_fats = Fat.objects.select_related('fatlink').filter(user=user).order_by('id')

    monthlystats = [0 for i in range(1, 13)]

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

    personal_fats = Fat.objects.filter(user=user)\
        .filter(fatlink__fatdatetime__gte=start_of_month).filter(fatlink__fatdatetime__lt=start_of_next_month)

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
def click_fatlink_view(request, token, fat_hash=None):
    fatlink = get_object_or_404(Fatlink, hash=fat_hash)

    if (timezone.now() - fatlink.fatdatetime) < datetime.timedelta(seconds=(fatlink.duration * 60)):

        character = EveCharacter.objects.get_character_by_id(token.character_id)

        if character:
            # get data
            c = token.get_esi_client(spec_file=SWAGGER_SPEC_PATH)
            location = c.Location.get_characters_character_id_location(character_id=token.character_id).result()
            ship = c.Location.get_characters_character_id_ship(character_id=token.character_id).result()
            location['solar_system_name'] = \
                c.Universe.get_universe_systems_system_id(system_id=location['solar_system_id']).result()[
                    'name']
            if location['station_id']:
                location['station_name'] = \
                    c.Universe.get_universe_stations_station_id(station_id=location['station_id']).result()['name']
            elif location['structure_id']:
                location['station_name'] = \
                    c.Universe.get_universe_structures_structure_id(structure_id=location['structure_id']).result()[
                        'name']
            else:
                location['station_name'] = "No Station"
            ship['ship_type_name'] = provider.get_itemtype(ship['ship_type_id']).name

            fat = Fat()
            fat.system = location['solar_system_name']
            fat.station = location['station_name']
            fat.shiptype = ship['ship_type_name']
            fat.fatlink = fatlink
            fat.character = character
            fat.user = request.user
            try:
                fat.full_clean()
                fat.save()
                messages.success(request, _('Fleet participation registered.'))
            except ValidationError as e:
                err_messages = []
                for errorname, message in e.message_dict.items():
                    err_messages.append(message[0])
                messages.error(request, ' '.join(err_messages))
        else:
            context = {'character_id': token.character_id,
                       'character_name': token.character_name}
            return render(request, 'fleetactivitytracking/characternotexisting.html', context=context)
    else:
        messages.error(request, _('FAT link has expired.'))
    return redirect('fatlink:view')


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
                fatlink.fleet = form.cleaned_data["fleet"]
                fatlink.duration = form.cleaned_data["duration"]
                fatlink.fatdatetime = timezone.now()
                fatlink.creator = request.user
                fatlink.hash = get_random_string(length=15)
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
                return render(request, 'fleetactivitytracking/fatlinkformatter.html', context=context)
            return redirect('fatlink:view')

    else:
        form = FatlinkForm()
        logger.debug("Returning empty form to user %s" % request.user)

    context = {'form': form}

    return render(request, 'fleetactivitytracking/fatlinkformatter.html', context=context)


@login_required
@permission_required('auth.fleetactivitytracking')
def modify_fatlink_view(request, fat_hash=None):
    logger.debug("modify_fatlink_view called by user %s" % request.user)
    fatlink = get_object_or_404(Fatlink, hash=fat_hash)

    if request.GET.get('removechar', None):
        character_id = request.GET.get('removechar')
        character = EveCharacter.objects.get(character_id=character_id)
        logger.debug("Removing character %s from fleetactivitytracking  %s" % (character.character_name, fatlink))

        Fat.objects.filter(fatlink=fatlink).filter(character=character).delete()

    if request.GET.get('deletefat', None):
        logger.debug("Removing fleetactivitytracking  %s" % fatlink)
        fatlink.delete()
        return redirect('fatlink:view')

    registered_fats = Fat.objects.select_related('character', 'fatlink', 'user')\
        .filter(fatlink=fatlink).order_by('character__character_name')

    context = {'fatlink': fatlink, 'registered_fats': registered_fats}

    return render(request, 'fleetactivitytracking/fatlinkmodify.html', context=context)
