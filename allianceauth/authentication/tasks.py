import logging

from esi.errors import TokenExpiredError, TokenInvalidError, IncompleteResponseError
from esi.models import Token
from celery import shared_task

from allianceauth.authentication.models import CharacterOwnership

logger = logging.getLogger(__name__)


@shared_task
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
            except (KeyError, IncompleteResponseError):
                # We can't validate the hash hasn't changed but also can't assume it has. Abort for now.
                logger.warning("Failed to validate owner hash of {0} due to problems contacting SSO servers.".format(
                    tokens[0].character_name))
                break

            if not t.character_owner_hash == old_hash:
                logger.info(
                    'Character %s has changed ownership. Revoking %s tokens.' % (t.character_name, tokens.count()))
                tokens.delete()
            break

    if not Token.objects.filter(character_owner_hash=owner_hash).exists():
        logger.info('No tokens found with owner hash %s. Revoking ownership.' % owner_hash)
        CharacterOwnership.objects.filter(owner_hash=owner_hash).delete()


@shared_task
def check_all_character_ownership():
    for c in CharacterOwnership.objects.all().only('owner_hash'):
        check_character_ownership.delay(c.owner_hash)
