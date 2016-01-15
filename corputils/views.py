from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import HttpResponseRedirect

from collections import namedtuple

from authentication.managers import AuthServicesInfoManager
from services.managers.eve_api_manager import EveApiManager
from eveonline.models import EveCorporationInfo
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo
from forms import CorputilsSearchForm

import logging

logger = logging.getLogger(__name__)


# Because corp-api only exist for the executor corp, this function will only be available in corporation mode.
@login_required
@permission_required('auth.corp_stats')
def corp_member_view(request):
    logger.debug("corp_member_view called by user %s" % request.user)
    # Get the corp the member is in
    auth_info = AuthServicesInfo.objects.get(user=request.user)
    logger.debug("Got user %s authservicesinfo model %s" % (request.user, auth_info))

    if settings.IS_CORP:
        corp = EveCorporationInfo.objects.get(corporation_id=settings.CORP_ID)

        member_list = EveApiManager.get_corp_membertracking()
        characters_with_api = {}
        characters_without_api = {}
        for char_id, member_data in member_list.items():
            try:
                char = EveCharacter.objects.get(character_id=char_id)
                user = char.user
                mainid = int(AuthServicesInfoManager.get_auth_service_info(user=user).main_char_id)
                mainname = EveCharacter.objects.get(character_id=mainid).character_name
                characters_with_api.setdefault(mainname,[]).append(char.character_name)
            except EveCharacter.DoesNotExist:
                characters_without_api.setdefault(member_data["name"],[]).append(member_data["name"])


        context = {"corp": corp,
                   "characters_with_api": sorted(characters_with_api.items()),
                   "characters_without_api": sorted(characters_without_api.items()),
                   "search_form": CorputilsSearchForm()}

        return render_to_response('registered/corputils.html',context, context_instance=RequestContext(request) )
    else:
        logger.error("Not running in corporation mode. Cannot provide corp member tracking data." % (request.user, auth_info.main_char_id))
    return render_to_response('registered/corputils.html', None, context_instance=RequestContext(request))


@login_required
@permission_required('auth.corp_stats')
def corputils_search(request):
    logger.debug("corputils_search called by user %s" % request.user)
    if request.method == 'POST':
        form = CorputilsSearchForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            # Really dumb search and only checks character name
            # This can be improved but it does the job for now
            searchstring = form.cleaned_data['search_string']
            logger.debug("Searching for player with character name %s for user %s" % (searchstring, request.user))

            member_list = EveApiManager.get_corp_membertracking()

            Member = namedtuple('Member', ['name', 'main', 'api_registered'])

            members = []
            for memberid, member_data in member_list.items():
                if searchstring.lower() in member_data["name"].lower():
                    try:
                        char = EveCharacter.objects.get(character_name=member_data["name"])
                        user = char.user
                        mainid = int(AuthServicesInfoManager.get_auth_service_info(user=user).main_char_id)
                        mainname = EveCharacter.objects.get(character_id=mainid).character_name
                        api_registered = True
                    except EveCharacter.DoesNotExist:
                        api_registered = False
                        mainname = ""
                    members.append(Member(name=member_data["name"], main=mainname, api_registered=api_registered))


            logger.info("Found %s members for user %s matching search string %s" % (len(members), request.user, searchstring))

            context = {'members': members, 'search_form': CorputilsSearchForm()}

            return render_to_response('registered/corputilssearchview.html',
                                      context, context_instance=RequestContext(request))
        else:
            logger.debug("Form invalid - returning for user %s to retry." % request.user)
            context = {'applications': None, 'search_form': form}
            return render_to_response('registered/corputilssearchview.html',
                                      context, context_instance=RequestContext(request))

    else:
        logger.debug("Returning empty search form for user %s" % request.user)
        return HttpResponseRedirect("/corputils/")

