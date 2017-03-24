from __future__ import unicode_literals
from django.conf import settings
from celery.task import periodic_task
from celery import task
from celery.task.schedules import crontab
from eveonline.managers import EveManager
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from eveonline.providers import ObjectNotFound
import logging

logger = logging.getLogger(__name__)

@task
def update_corp(corp_id, is_blue=None):
    EveManager.update_corporation(corp_id, is_blue=is_blue)


@task
def update_alliance(alliance_id, is_blue=None):
    EveManager.update_alliance(alliance_id, is_blue=is_blue)
    EveManager.populate_alliance(alliance_id)


@periodic_task(run_every=crontab(minute=0, hour="*/2"))
def run_corp_update():
    # generate member corps
    for corp_id in settings.STR_CORP_IDS + settings.STR_BLUE_CORP_IDS:
        is_blue = True if corp_id in settings.STR_BLUE_CORP_IDS else False
        try:
            if EveCorporationInfo.objects.filter(corporation_id=corp_id).exists():
                update_corp(corp_id, is_blue=is_blue)
            else:
                EveManager.create_corporation(corp_id, is_blue=is_blue)
        except ObjectNotFound:
            logger.warn('Bad corp ID in settings: %s' % corp_id)

    # generate member alliances
    for alliance_id in settings.STR_ALLIANCE_IDS + settings.STR_BLUE_ALLIANCE_IDS:
        is_blue = True if alliance_id in settings.STR_BLUE_ALLIANCE_IDS else False
        try:
            if EveAllianceInfo.objects.filter(alliance_id=alliance_id).exists():
                logger.debug("Updating existing owner alliance model with id %s" % alliance_id)
                update_alliance(alliance_id, is_blue=is_blue)
            else:
                EveManager.create_alliance(alliance_id, is_blue=is_blue)
                EveManager.populate_alliance(alliance_id)
        except ObjectNotFound:
            logger.warn('Bad alliance ID in settings: %s' % alliance_id)

    # update existing corp models
    for corp in EveCorporationInfo.objects.exclude(
            corporation_id__in=settings.STR_CORP_IDS + settings.STR_BLUE_CORP_IDS):
        update_corp.delay(corp.corporation_id)

    # update existing alliance models
    for alliance in EveAllianceInfo.objects.exclude(
            alliance_id__in=settings.STR_ALLIANCE_IDS + settings.STR_BLUE_ALLIANCE_IDS):
        update_alliance.delay(alliance.alliance_id)
