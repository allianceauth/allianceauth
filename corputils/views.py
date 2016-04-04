from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import HttpResponseRedirect

from collections import namedtuple

from authentication.managers import AuthServicesInfoManager
from services.managers.eve_api_manager import EveApiManager
from services.managers.evewho_manager import EveWhoManager
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCharacter
from eveonline.models import EveApiKeyPair
from authentication.models import AuthServicesInfo
from util import check_if_user_has_permission
from forms import CorputilsSearchForm
from evelink.api import APIError

import logging

logger = logging.getLogger(__name__)

@login_required
def corp_member_view(request, corpid = None):
    logger.debug("corp_member_view called by user %s" % request.user)

    try:
        user_main = EveCharacter.objects.get(character_id=AuthServicesInfoManager.get_auth_service_info(user=request.user).main_char_id)
        user_corp_id = int(user_main.corporation_id)
    except (ValueError, EveCharacter.DoesNotExist):
        user_corp_id = settings.CORP_ID


    if not settings.IS_CORP:
        alliance = EveAllianceInfo.objects.get(alliance_id=settings.ALLIANCE_ID)
        alliancecorps = EveCorporationInfo.objects.filter(alliance=alliance)
        membercorplist = [(int(membercorp.corporation_id), str(membercorp.corporation_name)) for membercorp in alliancecorps]
        membercorplist.sort(key=lambda tup: tup[1])
        membercorp_id_list = [int(membercorp.corporation_id) for membercorp in alliancecorps]

        bluecorps = EveCorporationInfo.objects.filter(is_blue=True)
        bluecorplist = [(int(bluecorp.corporation_id), str(bluecorp.corporation_name)) for bluecorp in bluecorps]
        bluecorplist.sort(key=lambda tup: tup[1])
        bluecorp_id_list = [int(bluecorp.corporation_id) for bluecorp in bluecorps]

        if not (user_corp_id in membercorp_id_list or user_corp_id not in bluecorp_id_list):
            user_corp_id = None

    if not corpid:
        if(settings.IS_CORP):
            corpid = settings.CORP_ID
        elif user_corp_id:
            corpid = user_corp_id
        else:
            corpid = membercorplist[0][0]

    corp = EveCorporationInfo.objects.get(corporation_id=corpid)
    Player = namedtuple("Player", ["main", "maincorp", "maincorpid", "altlist", "apilist"])

    if check_if_user_has_permission(request.user, 'alliance_apis') or (check_if_user_has_permission(request.user, 'corp_apis') and (user_corp_id == corpid)):
        logger.debug("Retreiving and sending API-information")

        if settings.IS_CORP:
            try:
                member_list = EveApiManager.get_corp_membertracking(settings.CORP_API_ID, settings.CORP_API_VCODE)
            except APIError:
                logger.debug("Corp API does not have membertracking scope, using EveWho data instead.")
                member_list = EveWhoManager.get_corporation_members(corpid)
        else:
            member_list = EveWhoManager.get_corporation_members(corpid)

        characters_with_api = {}
        characters_without_api = {}

        num_registered_characters = 0
        for char_id, member_data in member_list.items():
            try:
                char = EveCharacter.objects.get(character_id=char_id)
                char_owner = char.user
                try:
                    mainid = int(AuthServicesInfoManager.get_auth_service_info(user=char_owner).main_char_id)
                    mainchar = EveCharacter.objects.get(character_id=mainid)
                    mainname = mainchar.character_name
                    maincorp = mainchar.corporation_name
                    maincorpid = mainchar.corporation_id
                    api_pair = EveApiKeyPair.objects.get(api_id=char.api_id)
                except (ValueError, EveCharacter.DoesNotExist, EveApiKeyPair.DoesNotExist):
                    logger.info("No main character seem to be set for character %s" % char.character_name)
                    mainname = "User: " + char_owner.username
                    mainchar = char
                    maincorp = "Not set."
                    maincorpid = None
                    api_pair = None
                num_registered_characters = num_registered_characters + 1
                characters_with_api.setdefault(mainname, Player(main=mainchar,
                                                                maincorp=maincorp,
                                                                maincorpid=maincorpid,
                                                                altlist=[],
                                                                apilist=[])
                                               ).altlist.append(char)
                if api_pair:
                    characters_with_api[mainname].apilist.append(api_pair)

            except (EveCharacter.DoesNotExist):
                characters_without_api.update({member_data["name"]: member_data["id"]})

        for char in EveCharacter.objects.filter(corporation_id=corpid):
            if not char.character_id in member_list:
                logger.info("Character %s does not exist in EveWho dump." % char.character_name)
                char_owner = char.user
                try:
                    mainid = int(AuthServicesInfoManager.get_auth_service_info(user=char_owner).main_char_id)
                    mainchar = EveCharacter.objects.get(character_id=mainid)
                    mainname = mainchar.character_name
                    maincorp = mainchar.corporation_name
                    maincorpid = mainchar.corporation_id
                    api_pair = EveApiKeyPair.objects.get(api_id=char.api_id)
                except (ValueError, EveCharacter.DoesNotExist, EveApiKeyPair.DoesNotExist):
                    logger.info("No main character seem to be set for character %s" % char.character_name)
                    mainname = "User: " + char_owner.username
                    mainchar = char
                    maincorp = "Not set."
                    maincorpid = None
                    api_pair = None
                num_registered_characters = num_registered_characters + 1
                characters_with_api.setdefault(mainname, Player(main=mainchar,
                                                                maincorp=maincorp,
                                                                maincorpid=maincorpid,
                                                                altlist=[],
                                                                apilist=[])
                                               ).altlist.append(char)
                if api_pair:
                    characters_with_api[mainname].apilist.append(api_pair)

        n_unacounted = corp.member_count - (num_registered_characters + len(characters_without_api))

        if not settings.IS_CORP:
            context = {"membercorplist": membercorplist,
                       "corp": corp,
                       "characters_with_api": sorted(characters_with_api.items()),
                       'n_registered': num_registered_characters,
                       'n_unacounted': n_unacounted,
                       "characters_without_api": sorted(characters_without_api.items()),
                       "search_form": CorputilsSearchForm()}
        else:
            logger.debug("corp_member_view running in corportation mode")
            context = {"corp": corp,
                       "characters_with_api": sorted(characters_with_api.items()),
                       'n_registered': num_registered_characters,
                       'n_unacounted': n_unacounted,
                       "characters_without_api": sorted(characters_without_api.items()),
                       "search_form": CorputilsSearchForm()}

        return render_to_response('registered/corputils.html',context, context_instance=RequestContext(request) )
    return HttpResponseRedirect("/dashboard/")


@login_required
def corputils_search(request, corpid=settings.CORP_ID):
    logger.debug("corputils_search called by user %s" % request.user)

    corp = EveCorporationInfo.objects.get(corporation_id=corpid)

    authorized = False
    try:
        user_main = EveCharacter.objects.get(character_id=AuthServicesInfoManager.get_auth_service_info(user=request.user).main_char_id)
        if check_if_user_has_permission(request.user, 'alliance_apis') or (check_if_user_has_permission(request.user, 'corp_apis') and (user_main.corporation_id == corpid)):
            logger.debug("Retreiving and sending API-information")
            authorized = True
    except (ValueError, EveCharacter.DoesNotExist):
        if check_if_user_has_permission(request.user, 'alliance_apis'):
            logger.debug("Retreiving and sending API-information")
            authorized = True

    if authorized:
        if request.method == 'POST':
            form = CorputilsSearchForm(request.POST)
            logger.debug("Request type POST contains form valid: %s" % form.is_valid())
            if form.is_valid():
                # Really dumb search and only checks character name
                # This can be improved but it does the job for now
                searchstring = form.cleaned_data['search_string']
                logger.debug("Searching for player with character name %s for user %s" % (searchstring, request.user))

                if settings.IS_CORP:
                    try:
                        member_list = EveApiManager.get_corp_membertracking(settings.CORP_API_ID, settings.CORP_API_VCODE)
                    except APIError:
                        logger.debug("Corp API does not have membertracking scope, using EveWho data instead.")
                        member_list = EveWhoManager.get_corporation_members(corpid)
                else:
                    member_list = EveWhoManager.get_corporation_members(corpid)

                SearchResult = namedtuple('SearchResult', ['name', 'id', 'main', 'api_registered', 'character', 'apiinfo'])

                searchresults = []
                for memberid, member_data in member_list.items():
                    if searchstring.lower() in member_data["name"].lower():
                        try:
                            char = EveCharacter.objects.get(character_name=member_data["name"])
                            user = char.user
                            mainid = int(AuthServicesInfoManager.get_auth_service_info(user=user).main_char_id)
                            mainname = EveCharacter.objects.get(character_id=mainid).character_name
                            api_registered = True
                            apiinfo = EveApiKeyPair.objects.get(api_id=char.api_id)
                        except EveCharacter.DoesNotExist:
                            api_registered = False
                            char = None
                            mainname = ""
                            apiinfo = None

                        searchresults.append(SearchResult(name=member_data["name"], id=memberid, main=mainname, api_registered=api_registered,
                                                    character=char, apiinfo=apiinfo))


                logger.info("Found %s members for user %s matching search string %s" % (len(searchresults), request.user, searchstring))

                context = {'corp': corp, 'results': searchresults, 'search_form': CorputilsSearchForm()}

                return render_to_response('registered/corputilssearchview.html',
                                          context, context_instance=RequestContext(request))
            else:
                logger.debug("Form invalid - returning for user %s to retry." % request.user)
                context = {'corp': corp, 'members': None, 'search_form': CorputilsSearchForm()}
                return render_to_response('registered/corputilssearchview.html',
                                          context, context_instance=RequestContext(request))

        else:
            logger.debug("Returning empty search form for user %s" % request.user)
            return HttpResponseRedirect("/corputils/")
    return HttpResponseRedirect("/dashboard/")


