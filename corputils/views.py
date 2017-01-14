from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from eveonline.models import EveCharacter, EveCorporationInfo
from corputils.models import CorpStats
from esi.decorators import token_required
from bravado.exception import HTTPError

MEMBERS_PER_PAGE = int(getattr(settings, 'CORPSTATS_MEMBERS_PER_PAGE', 20))


def get_page(model_list, page_num):
    p = Paginator(model_list, MEMBERS_PER_PAGE)
    try:
        members = p.page(page_num)
    except PageNotAnInteger:
        members = p.page(1)
    except EmptyPage:
        members = p.page(p.num_pages)
    return members


def access_corpstats_test(user):
    return user.has_perm('corputils.view_corp_corpstats') or user.has_perm(
        'corputils.view_alliance_corpstats') or user.has_perm('corputils.view_blue_corpstats')


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
                token.get_esi_client().Character.get_characters_character_id(character_id=token.character_id).result()[
                    'corporation_id']
        corp = EveCorporationInfo.objects.get(corporation_id=corp_id)
        cs = CorpStats.objects.create(token=token, corp=corp)
        cs.update()
        assert cs.pk  # ensure update was succesful
        if CorpStats.objects.filter(pk=cs.pk).visible_to(request.user).exists():
            return redirect('corputils:view_corp', corp_id=corp.corporation_id)
    except EveCorporationInfo.DoesNotExist:
        messages.error(request, 'Unrecognized corporation. Please ensure it is a member of the alliance or a blue.')
    except IntegrityError:
        messages.error(request, 'Selected corp already has a statistics module.')
    except AssertionError:
        messages.error(request, 'Failed to gather corporation statistics with selected token.')
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
    available = CorpStats.objects.visible_to(request.user)

    # ensure we can see the requested model
    if corpstats and corpstats not in available:
        raise PermissionDenied('You do not have permission to view the selected corporation statistics module.')

    # get default model if none requested
    if not corp_id and available.count() == 1:
        corpstats = available[0]

    context = {
        'available': available,
    }

    # paginate
    members = []
    if corpstats:
        page = request.GET.get('page', 1)
        members = get_page(corpstats.get_member_objects(request.user), page)

    if corpstats:
        context.update({
            'corpstats': corpstats.get_view_model(request.user),
            'members': members,
        })

    return render(request, 'corputils/corpstats.html', context=context)


@login_required
@user_passes_test(access_corpstats_test)
def corpstats_update(request, corp_id):
    corp = get_object_or_404(EveCorporationInfo, corporation_id=corp_id)
    corpstats = get_object_or_404(CorpStats, corp=corp)
    if corpstats.can_update(request.user):
        try:
            corpstats.update()
        except HTTPError as e:
            messages.error(request, str(e))
    else:
        raise PermissionDenied(
            'You do not have permission to update member data for the selected corporation statistics module.')
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
        has_similar = CorpStats.objects.filter(_members__icontains=search_string).visible_to(request.user)
        for corpstats in has_similar:
            similar = [(member_id, corpstats.members[member_id]) for member_id in corpstats.members if
                       search_string.lower() in corpstats.members[member_id].lower()]
            for s in similar:
                results.append(
                    (corpstats, CorpStats.MemberObject(s[0], s[1], show_apis=corpstats.show_apis(request.user))))
        page = request.GET.get('page', 1)
        results = sorted(results, key=lambda x: x[1].character_name)
        results_page = get_page(results, page)
        context = {
            'available': CorpStats.objects.visible_to(request.user),
            'results': results_page,
            'search_string': search_string,
        }
        return render(request, 'corputils/search.html', context=context)
    return redirect('corputils:view')
