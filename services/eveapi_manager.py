import evelink.api
import evelink.char
import evelink.eve


class EveApiManager():

    def __init__(self):
        pass


    def get_characters_from_api(self, api_id, api_key):
        api = evelink.api.API(api_key=(api_id, api_key))
        # Should get characters
        account = evelink.account.Account(api=api)
        chars = account.characters()

        return chars

