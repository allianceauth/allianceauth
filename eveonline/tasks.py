from __future__ import unicode_literals
from eveonline.managers import EveManager
from eveonline.models import EveCorporationInfo
from eveonline.models import EveAllianceInfo
from eveonline.models import EveCharacter
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
def update_character(character_id):
    EveManager.update_character(character_id)


@app.task
def run_model_update():
    # update existing corp models
    for corp in EveCorporationInfo.objects.all().values('corporation_id'):
        update_corp.delay(corp['corporation_id'])

    # update existing alliance models
    for alliance in EveAllianceInfo.objects.all().values('alliance_id'):
        update_alliance.delay(alliance['alliance_id'])

    for character in EveCharacter.objects.all().values('character_id'):
        update_character.delay(character['character_id'])
