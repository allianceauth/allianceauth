import evelink.api
import evelink.char
import evelink.eve


class EveApiManager():

    def __init__(self):
        pass

    @staticmethod
    def get_characters_from_api(api_id, api_key):
        chars = []
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            # Should get characters
            account = evelink.account.Account(api=api)
            chars = account.characters()
        except evelink.api.APIError as error:
            print error

        return chars

    @staticmethod
    def get_corporation_ticker_from_id(corp_id):
        ticker = ""
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api)
            response = corp.corporation_sheet(corp_id)
            ticker = response[0]['ticker']
        except evelink.api.APIError as error:
            print error

        return ticker

    @staticmethod
    def check_api_is_type_account(api_id, api_key):
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            return info[0]['type'] == "account"

        except evelink.api.APIError as error:
            print error

        return False


    @staticmethod
    def check_api_is_full(api_id, api_key):
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            return info[0]['access_mask'] == 268435455

        except evelink.api.APIError as error:
            print error

        return False


    @staticmethod
    def get_api_info(api_id, api_key):
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.key_info()
            return info

        except evelink.api.APIError as error:
            print error

        return False

    @staticmethod
    def api_key_is_valid(api_id, api_key):
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            account = evelink.account.Account(api=api)
            info = account.status()
            return True
        except evelink.api.APIError as error:
            return False

        return False