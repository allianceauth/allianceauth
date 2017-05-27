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

from alliance_auth.celeryapp import app

logger = logging.getLogger(__name__)

@app.task
def update_corp(corp_id):
    EveManager.update_corporation(corp_id)


@app.task
def update_alliance(alliance_id):
    EveManager.update_alliance(alliance_id)
    EveManager.populate_alliance(alliance_id)


@app.task
def run_corp_update():
    # generate member corps
    for corp_id in settings.STR_CORP_IDS + settings.STR_BLUE_CORP_IDS:
        try:
            if EveCorporationInfo.objects.filter(corporation_id=corp_id).exists():
                update_corp.apply(arge=[corp_id])
            else:
                EveManager.create_corporation(corp_id)
        except ObjectNotFound:
            logger.warn('Bad corp ID in settings: %s' % corp_id)

    # generate member alliances
    for alliance_id in settings.STR_ALLIANCE_IDS + settings.STR_BLUE_ALLIANCE_IDS:
        try:
            if EveAllianceInfo.objects.filter(alliance_id=alliance_id).exists():
                logger.debug("Updating existing owner alliance model with id %s" % alliance_id)
                update_alliance.apply(args=[alliance_id])
            else:
                EveManager.create_alliance(alliance_id)
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
