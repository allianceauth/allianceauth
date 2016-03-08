import evelink.api
import evelink.char
import evelink.eve

from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class EveApiManager():
    def __init__(self):
        pass

    @staticmethod
    def get_characters_from_api(api_id, api_key):
        chars = []
        logger.debug("Getting characters from api id %s" % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            # Should get characters
            account = evelink.account.Account(api=api)
            chars = account.characters()
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")

        logger.debug("Retrieved characters %s from api id %s" % (chars, api_id))
        return chars

    @staticmethod
    def get_corporation_ticker_from_id(corp_id):
        logger.debug("Getting ticker for corp id %s" % corp_id)
        ticker = ""
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api)
            response = corp.corporation_sheet(corp_id)
            logger.debug("Retrieved corp sheet for id %s: %s" % (corp_id, response))
            ticker = response[0]['ticker']
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")

        logger.debug("Determined corp id %s ticker: %s" % (corp_id, ticker))
        return ticker

    @staticmethod
    def get_alliance_information(alliance_id):
        results = {}
        logger.debug("Getting info for alliance with id %s" % alliance_id)
        try:
            api = evelink.api.API()
            eve = evelink.eve.EVE(api=api)
            alliance = eve.alliances()
            results = alliance[0][int(alliance_id)]
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
        logger.debug("Got alliance info %s" % results)
        return results

    @staticmethod
    def get_corporation_information(corp_id):
        logger.debug("Getting info for corp with id %s" % corp_id)
        results = {}
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api=api)
            corpinfo = corp.corporation_sheet(corp_id=int(corp_id))
            results = corpinfo[0]
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
        logger.debug("Got corp info %s" % results)
        return results

    @staticmethod
    def check_api_is_type_account(api_id, api_key):
        logger.debug("Checking if api id %s is account." % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            logger.debug("API id %s is type %s" % (api_id, info[0]['type']))
            return info[0]['type'] == "account"

        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
            return None


    @staticmethod
    def check_api_is_full(api_id, api_key):
        logger.debug("Checking if api id %s meets member requirements." % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            logger.debug("API has mask %s, required is %s" % (info[0]['access_mask'], settings.MEMBER_API_MASK))
            return info[0]['access_mask'] & int(settings.MEMBER_API_MASK) == int(settings.MEMBER_API_MASK)

        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
            return None

    @staticmethod
    def check_blue_api_is_full(api_id, api_key):
        logger.debug("Checking if api id %s meets blue requirements." % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            logger.debug("API has mask %s, required is %s" % (info[0]['access_mask'], settings.BLUE_API_MASK))
            return info[0]['access_mask'] & int(settings.BLUE_API_MASK) == int(settings.BLUE_API_MASK)
 
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
            return None


    @staticmethod
    def get_api_info(api_id, api_key):
        logger.debug("Getting api info for key id %s" % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            logger.debug("Got info for api id %s: %s" % (api_id, info))
            return info

        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
            return None

    @staticmethod
    def api_key_is_valid(api_id, api_key):
        logger.debug("Checking if api id %s is valid." % api_id)
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            logger.info("Verified api id %s is still valid." % api_id)
            return True
        except evelink.api.APIError as error:
            logger.exception("APIError occured while validating api id %s" % api_id)

        logger.info("API id %s is invalid." % api_id)
        return False

    @staticmethod
    def check_if_api_server_online():
        logger.debug("Checking if API server online.")
        try:
            api = evelink.api.API()
            server = evelink.server.Server(api=api)
            info = server.server_status()
            logger.info("Verified API server is online and reachable.")
            return True
        except evelink.api.APIError as error:
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
            results = corpinfo[0]
            logger.debug("Confirmed id %s is a corp." % corp_id)
            return True
        except evelink.api.APIError as error:
            logger.debug("APIError occured while checking if id %s is corp. Possibly not corp?" % corp_id)

        logger.debug("Unable to verify id %s is corp." % corp_id)
        return False

    @staticmethod
    def get_corp_standings():
        if settings.CORP_API_ID and settings.CORP_API_VCODE:
            try:
                logger.debug("Getting corp standings with api id %s" % settings.CORP_API_ID)
                api = evelink.api.API(api_key=(settings.CORP_API_ID, settings.CORP_API_VCODE))
                corp = evelink.corp.Corp(api=api)
                corpinfo = corp.contacts()
                results = corpinfo.result
                logger.debug("Got corp standings from settings: %s" % results)
                return results
            except evelink.api.APIError as error:
                logger.exception("Unhandled APIError occured.", exc_info=True)
        else:
            logger.error("No corp API key supplied in settings. Unable to get standings.")
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
        except evelink.api.APIError as error:
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
        except evelink.api.APIError as error:
            logger.exception("APIError occured while checking if id %s is an alliance. Possibly not alliance?" % alliance_id)
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
        except evelink.api.APIError as error:
            logger.debug("APIError occured while checking if id %s is a character. Possibly not character?" % character_id, exc_info=True)

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
        except evelink.api.APIError as error:
            logger.exception("Unhandled APIError occured.")
            return False
        except ValueError as error:
            #attempts to catch error resulting from checking alliance_of nonetype models
            logger.exception("Unhandled ValueError occured. Possible nonetype alliance model.")
            return False
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
                logger.debug("Verified corp id %s exists with member count %s" % (corp_id, corpinfo[0]['members']['current']))
                return True
            else:
                logger.debug("Verified corp id %s has closed. Member count %s" % (corp_id, corpinfo[0]['members']['current']))
                return False
        except evelink.api.APIError as error:
            #could be smart and check for error code523 to verify error due to no corp instead of catch-all
            logger.exception("Unhandled APIError occured.")
            return False
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
