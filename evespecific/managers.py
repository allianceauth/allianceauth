from models import EveCharacter
from models import EveApiKeyPair
from services.eveapi_manager import EveApiManager


class EveManager():
    
    def __init__(self):
        pass
    
    def create_character(self, character_id, character_name, corporation_id,
                         corporation_name,  corporation_ticker, alliance_id,
                         alliance_name, user, api_id):

        if not EveCharacter.objects.filter(character_id=character_id).exists():
            eve_char = EveCharacter();
            eve_char.character_id = character_id
            eve_char.character_name = character_name
            eve_char.corporation_id = corporation_id
            eve_char.corporation_name = corporation_name
            eve_char.corporation_ticker = corporation_ticker
            eve_char.alliance_id = alliance_id
            eve_char.alliance_name = alliance_name
            eve_char.user = user
            eve_char.api_id = api_id
            eve_char.save()

    def create_characters_from_list(self, chars, user, api_id):
        evemanager = EveApiManager()

        for char in chars.result:
            if not self.check_if_character_exist(chars.result[char]['name']):
                self.create_character(chars.result[char]['id'],
                                      chars.result[char]['name'],
                                      chars.result[char]['corp']['id'],
                                      chars.result[char]['corp']['name'],
                                      evemanager.get_corporation_ticker_from_id(chars.result[char]['corp']['id']),
                                      chars.result[char]['alliance']['id'],
                                      chars.result[char]['alliance']['name'],
                                      user, api_id)

    def create_api_keypair(self, api_id, api_key, user_id):
        if not EveApiKeyPair.objects.filter(api_id=api_id).exists():
            api_pair = EveApiKeyPair()
            api_pair.api_id = api_id
            api_pair.api_key = api_key
            api_pair.user = user_id
            api_pair.save()

    def get_api_key_pairs(self, user_id):
        if EveApiKeyPair.objects.filter(user=user_id).exists():
            return EveApiKeyPair.objects.filter(user=user_id)

    def delete_api_key_pair(self, api_id, user_id):
        if EveApiKeyPair.objects.filter(api_id=api_id).exists():
            # Check that its owned by our user_id
            apikeypair = EveApiKeyPair.objects.get(api_id=api_id)
            if apikeypair.user.id == user_id:
                apikeypair.delete()

    def delete_characters_by_api_id(self, api_id, user_id):
        if EveCharacter.objects.filter(api_id=api_id).exists():
            # Check that its owned by our user_id
            characters = EveCharacter.objects.filter(api_id=api_id)

            for char in characters:
                if char.user.id == user_id:
                    char.delete()


    def check_if_character_exist(self, char_name):
        return EveCharacter.objects.filter(character_name=char_name).exists()

    def get_characters_by_owner_id(self, user_id):
        return EveCharacter.objects.all().filter(user_id=user_id)
    
    def get_character_by_id(self, char_id):
        if EveCharacter.objects.filter(character_id = char_id).exists():
            return EveCharacter.objects.get(character_id=char_id)
        
        return None
    
    def check_if_character_owned_by_user(self, char_id, user_id):
        character = EveCharacter.objects.get(character_id = char_id)

        if character.allianceuser_owner.id == user_id:
            return True
        
        return False