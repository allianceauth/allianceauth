import sys
import evelink.api
import evelink.char
import evelink.eve


class EveApiManager():

    def __init__(self):
        pass

    def get_characters_from_api(self, api_id, api_key):
        chars = []
        try:
            api = evelink.api.API(api_key=(api_id, api_key))
            # Should get characters
            account = evelink.account.Account(api=api)
            chars = account.characters()
        except evelink.api.APIError as error:
            print error

        return chars

    def get_corporation_ticker_from_id(self, corp_id):
        ticker = ""
        try:
            print corp_id
            api = evelink.api.API()
            corp = evelink.corp.Corp(api)
            response = corp.corporation_sheet(corp_id)
            print response
            ticker = response[0]['ticker']
        except evelink.api.APIError as error:
            print error

        return ticker


