import os

from bravado.exception import HTTPError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from esi.decorators import token_required
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

from .models import CorpStats

SWAGGER_SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')
"""
Swagger spec operations:

get_characters_character_id
"""


def access_corpstats_test(user):
    return user.has_perm('corputils.view_corp_corpstats') or user.has_perm(
        'corputils.view_alliance_corpstats') or user.has_perm('corputils.view_state_corpstats') or user.has_perm(
        'corputils.add_corpstats')


@login_required
@user_passes_test(access_corpstats_test)
@permission_required('corputils.add_corpstats')
@token_required(scopes='esi-corporations.read_corporation_membership.v1')
def corpstats_add(request, token):
    try:
        if EveCharacter.objects.filter(character_id=token.character_id).exists():
            corp_id = EveCharacter.objects.get(character_id=token.character_id).corporation_id
        else:
            corp_id = \
                token.get_esi_client(spec_file=SWAGGER_SPEC_PATH).Character.get_characters_character_id(
                    character_id=token.character_id).result()['corporation_id']
        try:
            corp = EveCorporationInfo.objects.get(corporation_id=corp_id)
        except EveCorporationInfo.DoesNotExist:
            corp = EveCorporationInfo.objects.create_corporation(corp_id)
        cs = CorpStats.objects.create(token=token, corp=corp)
        try:
            cs.update()
        except HTTPError as e:
            messages.error(request, str(e))
        assert cs.pk  # ensure update was successful
        if CorpStats.objects.filter(pk=cs.pk).visible_to(request.user).exists():
            return redirect('corputils:view_corp', corp_id=corp.corporation_id)
    except IntegrityError:
        messages.error(request, _('Selected corp already has a statistics module.'))
    except AssertionError:
        messages.error(request, _('Failed to gather corporation statistics with selected token.'))
    return redirect('corputils:view')


@login_required
@user_passes_test(access_corpstats_test)
def corpstats_view(request, corp_id=None):
    corpstats = None

    # get requested model
    if corp_id:
        corp = get_object_or_404(EveCorporationInfo, corporation_id=corp_id)
        corpstats = get_object_or_404(CorpStats, corp=corp)

    # get available models
    available = CorpStats.objects.visible_to(request.user).order_by('corp__corporation_name')

    # ensure we can see the requested model
    if corpstats and corpstats not in available:
        raise PermissionDenied('You do not have permission to view the selected corporation statistics module.')

    # get default model if none requested
    if not corp_id and available.count() == 1:
        corpstats = available[0]
    elif not corp_id and available.count() > 1 and request.user.profile.main_character:
        # get their main corp if available
        try:
            corpstats = available.get(corp__corporation_id=request.user.profile.main_character.corporation_id)
        except CorpStats.DoesNotExist:
            pass

    context = {
        'available': available,
    }

    if corpstats:
        members = corpstats.members.all()
        mains = corpstats.mains.all()
        unregistered = corpstats.unregistered_members.all()
        context.update({
            'corpstats': corpstats,
            'members': members,
            'mains': mains,
            'unregistered': unregistered,
        })

    return render(request, 'corputils/corpstats.html', context=context)


@login_required
@user_passes_test(access_corpstats_test)
def corpstats_update(request, corp_id):
    corp = get_object_or_404(EveCorporationInfo, corporation_id=corp_id)
    corpstats = get_object_or_404(CorpStats, corp=corp)
    try:
        corpstats.update()
    except HTTPError as e:
        messages.error(request, str(e))
    if corpstats.pk:
        return redirect('corputils:view_corp', corp_id=corp.corporation_id)
    else:
        return redirect('corputils:view')


@login_required
@user_passes_test(access_corpstats_test)
def corpstats_search(request):
    results = []
    search_string = request.GET.get('search_string', None)
    if search_string:
        has_similar = CorpStats.objects.filter(members__character_name__icontains=search_string).visible_to(
            request.user).distinct()
        for corpstats in has_similar:
            similar = corpstats.members.filter(character_name__icontains=search_string)
            for s in similar:
                results.append((corpstats, s))
        results = sorted(results, key=lambda x: x[1].character_name)
        context = {
            'available': CorpStats.objects.visible_to(request.user),
            'results': results,
            'search_string': search_string,
        }
        return render(request, 'corputils/search.html', context=context)
    return redirect('corputils:view')
