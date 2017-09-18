import logging

from esi.errors import TokenExpiredError, TokenInvalidError
from esi.models import Token

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.celeryapp import app

logger = logging.getLogger(__name__)


@app.task
def check_character_ownership(owner_hash):
    tokens = Token.objects.filter(character_owner_hash=owner_hash)
    if tokens:
        for t in tokens:
            old_hash = t.character_owner_hash
            try:
                t.update_token_data(commit=False)
            except (TokenExpiredError, TokenInvalidError):
                t.delete()
                continue

            if t.character_owner_hash == old_hash:
                break
            else:
                logger.info('Character %s has changed ownership. Revoking %s tokens.' % (t.character_name, tokens.count()))
                tokens.delete()
    else:
        logger.info('No tokens found with owner hash %s. Revoking ownership.' % owner_hash)
        CharacterOwnership.objects.filter(owner_hash=owner_hash).delete()


@app.task
def check_all_character_ownership():
    for c in CharacterOwnership.objects.all().only('owner_hash'):
        check_character_ownership.delay(c.owner_hash)
