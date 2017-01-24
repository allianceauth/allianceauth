from __future__ import unicode_literals
import evelink.api
import evelink.char
import evelink.eve
from authentication.states import MEMBER_STATE, BLUE_STATE
from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter
from django.conf import settings
import requests
try:
    from urllib2 import HTTPError, URLError
except ImportError: # py3
    from urllib.error import URLError, HTTPError

import logging

logger = logging.getLogger(__name__)


class EveApiManager:
    def __init__(self):
        pass

    class ApiValidationError(Exception):
        def __init__(self, msg, api_id):
            self.msg = msg
            self.api_id = api_id

        def __str__(self):
            return self.msg

    class ApiMaskValidationError(ApiValidationError):
        def __init__(self, required_mask, api_mask, api_id):
            msg = 'Insufficient API mask provided. Required: %s Got: %s' % (required_mask, api_mask)
            self.required_mask = required_mask
            self.api_mask = api_mask
            super(EveApiManager.ApiMaskValidationError, self).__init__(msg, api_id)

    class ApiAccountValidationError(ApiValidationError):
        def __init__(self, api_id):
            msg = 'Insufficient API access provided. Full account access is required, got character restricted.'
            super(EveApiManager.ApiAccountValidationError, self).__init__(msg, api_id)

    class ApiInvalidError(ApiValidationError):
        def __init__(self, api_id):
            msg = 'Key is invalid.'
            super(EveApiManager.ApiInvalidError, self).__init__(msg, api_id)

    class ApiServerUnreachableError(Exception):
        def __init__(self, e):
            self.error = e

        def __str__(self):
            return 'Unable to reach API servers: %s' % str(self.error)

    @staticmethod
    def get_characters_from_api(api_id, api_key):
        logger.debug("Getting characters from api id %s" % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        # Should get characters
        account = evelink.account.Account(api=api)
        chars = account.characters()
        logger.debug("Retrieved characters %s from api id %s" % (chars, api_id))
        return chars

    @staticmethod
    def get_corporation_ticker_from_id(corp_id):
        logger.debug("Getting ticker for corp id %s" % corp_id)
        api = evelink.api.API()
        corp = evelink.corp.Corp(api)
        response = corp.corporation_sheet(corp_id)
        logger.debug("Retrieved corp sheet for id %s: %s" % (corp_id, response))
        ticker = response[0]['ticker']
        logger.debug("Determined corp id %s ticker: %s" % (corp_id, ticker))
        return ticker

    @staticmethod
    def get_alliance_information(alliance_id):
        logger.debug("Getting info for alliance with id %s" % alliance_id)
        api = evelink.api.API()
        eve = evelink.eve.EVE(api=api)
        alliance = eve.alliances()
        results = alliance[0][int(alliance_id)]
        logger.debug("Got alliance info %s" % results)
        return results

    @staticmethod
    def get_corporation_information(corp_id):
        logger.debug("Getting info for corp with id %s" % corp_id)
        api = evelink.api.API()
        corp = evelink.corp.Corp(api=api)
        corpinfo = corp.corporation_sheet(corp_id=int(corp_id))
        results = corpinfo[0]
        logger.debug("Got corp info %s" % results)
        return results

    @staticmethod
    def get_api_info(api_id, api_key):
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        return account.key_info()[0]

    @staticmethod
    def check_api_is_type_account(api_id, api_key):
        logger.debug("Checking if api id %s is account." % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        info = account.key_info()
        logger.debug("API id %s is type %s" % (api_id, info[0]['type']))
        return info[0]['type'] == "account"

    @staticmethod
    def check_api_is_full(api_id, api_key):
        logger.debug("Checking if api id %s meets member requirements." % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        info = account.key_info()
        logger.debug("API has mask %s, required is %s" % (info[0]['access_mask'], settings.MEMBER_API_MASK))
        return info[0]['access_mask'] & int(settings.MEMBER_API_MASK) == int(settings.MEMBER_API_MASK)

    @staticmethod
    def check_blue_api_is_full(api_id, api_key):
        logger.debug("Checking if api id %s meets blue requirements." % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        info = account.key_info()
        logger.debug("API has mask %s, required is %s" % (info[0]['access_mask'], settings.BLUE_API_MASK))
        return info[0]['access_mask'] & int(settings.BLUE_API_MASK) == int(settings.BLUE_API_MASK)

    @staticmethod
    def get_api_info(api_id, api_key):
        logger.debug("Getting api info for key id %s" % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        info = account.key_info()
        logger.debug("Got info for api id %s: %s" % (api_id, info))
        return info

    @staticmethod
    def api_key_is_valid(api_id, api_key):
        logger.debug("Checking if api id %s is valid." % api_id)
        api = evelink.api.API(api_key=(api_id, api_key))
        account = evelink.account.Account(api=api)
        account.key_info()
        logger.info("Verified api id %s is still valid." % api_id)
        return True

    @staticmethod
    def check_if_api_server_online():
        logger.debug("Checking if API server online.")
        try:
            api = evelink.api.API()
            server = evelink.server.Server(api=api)
            server.server_status()
            logger.info("Verified API server is online and reachable.")
            return True
        except evelink.api.APIError:
            logger.exception("APIError occured while trying to query api server. Possibly offline?")

        logger.warn("Unable to reach API server.")
        return False

    @staticmethod
    def check_if_id_is_corp(corp_id):
        logger.debug("Checking if id %s is a corp." % corp_id)
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api=api)
            corpinfo = corp.corporation_sheet(corp_id=int(corp_id))
            assert corpinfo[0]
            logger.debug("Confirmed id %s is a corp." % corp_id)
            return True
        except evelink.api.APIError as error:
            if int(error.code) == '523':
                logger.debug("Confirmed id %s is not a corp" % corp_id)
                return False
            logger.debug("APIError occured while checking if id %s is corp. Possibly not corp?" % corp_id)

        logger.debug("Unable to verify id %s is corp." % corp_id)
        return False

    @staticmethod
    def get_corp_standings():
        if settings.CORP_API_ID and settings.CORP_API_VCODE:
            logger.debug("Getting corp standings with api id %s" % settings.CORP_API_ID)
            api = evelink.api.API(api_key=(settings.CORP_API_ID, settings.CORP_API_VCODE))
            corp = evelink.corp.Corp(api=api)
            corpinfo = corp.contacts()
            results = corpinfo.result
            logger.debug("Got corp standings from settings: %s" % results)
            return results
        else:
            logger.warn("No corp API key supplied in settings. Unable to get standings.")
        return {}

    @staticmethod
    def get_corp_membertracking(api, vcode):
        try:
            logger.debug("Getting corp membertracking with api id %s" % settings.CORP_API_ID)
            api = evelink.api.API(api_key=(api, vcode))
            corp = evelink.corp.Corp(api=api)
            membertracking = corp.members()
            results = membertracking.result
            logger.debug("Got corp membertracking from settings: %s" % results)
            return results
        except evelink.api.APIError:
            logger.exception("Unhandled APIError occured.")
        return {}

    @staticmethod
    def check_if_id_is_alliance(alliance_id):
        logger.debug("Checking if id %s is an alliance." % alliance_id)
        try:
            api = evelink.api.API()
            eve = evelink.eve.EVE(api=api)
            alliance = eve.alliances()
            results = alliance.result[int(alliance_id)]
            if results:
                logger.debug("Confirmed id %s is an alliance." % alliance_id)
                return True
        except evelink.api.APIError:
            logger.exception(
                "APIError occured while checking if id %s is an alliance. Possibly not alliance?" % alliance_id)
        except KeyError:
            logger.debug("Alliance with id %s not found in active alliance list." % alliance_id)
            return False
        logger.debug("Unable to verify id %s is an an alliance." % alliance_id)
        return False

    @staticmethod
    def check_if_id_is_character(character_id):
        logger.debug("Checking if id %s is a character." % character_id)
        try:
            api = evelink.api.API()
            eve = evelink.eve.EVE(api=api)
            results = eve.character_info_from_id(character_id)
            if results:
                logger.debug("Confirmed id %s is a character." % character_id)
                return True
        except evelink.api.APIError:
            logger.debug(
                "APIError occured while checking if id %s is a character. Possibly not character?" % character_id,
                exc_info=True)

        logger.debug("Unable to verify id %s is a character." % character_id)
        return False

    @staticmethod
    def check_if_alliance_exists(alliance_id):
        logger.debug("Checking if alliance id %s exists." % alliance_id)
        try:
            api = evelink.api.API()
            eve = evelink.eve.EVE(api=api)
            alliances = eve.alliances()
            if int(alliance_id) in alliances[0]:
                logger.debug("Verified alliance id %s exists." % alliance_id)
                return True
            else:
                logger.debug("Verified alliance id %s does not exist." % alliance_id)
                return False
        except evelink.api.APIError:
            logger.exception("Unhandled APIError occured.")
            return False
        except ValueError:
            # attempts to catch error resulting from checking alliance_of nonetype models
            logger.exception("Unhandled ValueError occured. Possible nonetype alliance model.")
            return False
        except:
            logger.warn("Exception prevented verification of alliance id %s existance. Assuming false." % alliance_id)
            return False

    @staticmethod
    def check_if_corp_exists(corp_id):
        logger.debug("Checking if corp id %s exists." % corp_id)
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api=api)
            corpinfo = corp.corporation_sheet(corp_id=corp_id)
            if corpinfo[0]['members']['current'] > 0:
                logger.debug(
                    "Verified corp id %s exists with member count %s" % (corp_id, corpinfo[0]['members']['current']))
                return True
            else:
                logger.debug(
                    "Verified corp id %s has closed. Member count %s" % (corp_id, corpinfo[0]['members']['current']))
                return False
        except evelink.api.APIError:
            # could be smart and check for error code523 to verify error due to no corp instead of catch-all
            logger.exception("Unhandled APIError occured.")
            return False
        except:
            logger.warn("Exception prevented verification of corp id %s existance. Assuming false." % corp_id)
            return False

    @staticmethod
    def validate_member_api(api_id, api_key):
        if settings.MEMBER_API_ACCOUNT:
            if EveApiManager.check_api_is_type_account(api_id, api_key) is False:
                logger.info("Api id %s is not type account as required for members - failed validation." % api_id)
                return False

        if EveApiManager.check_api_is_full(api_id, api_key) is False:
            logger.info("Api id %s does not meet member access mask requirements - failed validation." % api_id)
            return False
        return True

    @staticmethod
    def validate_blue_api(api_id, api_key):
        if settings.BLUE_API_ACCOUNT:
            if EveApiManager.check_api_is_type_account(api_id, api_key) is False:
                logger.info("Api id %s is not type account as required for blues - failed validation." % api_id)
                return False
        if EveApiManager.check_blue_api_is_full(api_id, api_key) is False:
            logger.info("Api id %s does not meet minimum blue access mask requirements - failed validation." % api_id)
            return False
        return True

    @staticmethod
    def validate_api(api_id, api_key, user):
        try:
            info = EveApiManager.get_api_info(api_id, api_key).result
        except evelink.api.APIError as e:
            if int(e.code) == 222:
                raise EveApiManager.ApiInvalidError(api_id)
            raise e
        except (requests.exceptions.RequestException, HTTPError, URLError) as e:
            raise EveApiManager.ApiServerUnreachableError(e)
        auth = AuthServicesInfo.objects.get(user=user)
        states = [auth.state]
        from authentication.tasks import determine_membership_by_character  # circular import issue
        chars = info['characters']
        for char in chars:
            evechar = EveCharacter()
            evechar.character_name = chars[char]['name']
            evechar.corporation_id = chars[char]['corp']['id']
            evechar.alliance_id = chars[char]['alliance']['id']
            states.append(determine_membership_by_character(evechar))
        if MEMBER_STATE not in states and BLUE_STATE not in states:
            # default to requiring member keys for applications
            states.append(MEMBER_STATE)
        logger.debug('Checking API %s for states %s' % (api_id, states))
        for state in states:
            if (state == MEMBER_STATE and settings.MEMBER_API_ACCOUNT) or (
                            state == BLUE_STATE and settings.BLUE_API_ACCOUNT):
                if info['type'] != 'account':
                    raise EveApiManager.ApiAccountValidationError(api_id)
            if state == MEMBER_STATE:
                if int(info['access_mask']) & int(settings.MEMBER_API_MASK) != int(settings.MEMBER_API_MASK):
                    raise EveApiManager.ApiMaskValidationError(settings.MEMBER_API_MASK, info['access_mask'], api_id)
            elif state == BLUE_STATE:
                if int(info['access_mask']) & int(settings.BLUE_API_MASK) != int(settings.BLUE_API_MASK):
                    raise EveApiManager.ApiMaskValidationError(settings.BLUE_API_MASK, info['access_mask'], api_id)
        return True
