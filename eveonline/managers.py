from models import EveCharacter
from models import EveApiKeyPair
from services.managers.eve_api_manager import EveApiManager


class EveManager:
    
    def __init__(self):
        pass

    @staticmethod
    def create_character(character_id, character_name, corporation_id,
                         corporation_name,  corporation_ticker, alliance_id,
                         alliance_name, user, api_id):

        if not EveCharacter.objects.filter(character_id=character_id).exists():
            eve_char = EveCharacter()
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

    @staticmethod
    def create_characters_from_list(chars, user, api_id):

        for char in chars.result:
            if not EveManager.check_if_character_exist(chars.result[char]['name']):
                EveManager.create_character(chars.result[char]['id'],
                                      chars.result[char]['name'],
                                      chars.result[char]['corp']['id'],
                                      chars.result[char]['corp']['name'],
                                      EveApiManager.get_corporation_ticker_from_id(chars.result[char]['corp']['id']),
                                      chars.result[char]['alliance']['id'],
                                      chars.result[char]['alliance']['name'],
                                      user, api_id)

    @staticmethod
    def update_characters_from_list(chars):
        for char in chars.result:
            if EveManager.check_if_character_exist(chars.result[char]['name']):
                eve_char = EveManager.get_character_by_character_name(chars.result[char]['name'])
                eve_char.corporation_id = chars.result[char]['corp']['id']
                eve_char.corporation_name = chars.result[char]['corp']['name']
                eve_char.corporation_ticker = EveApiManager.get_corporation_ticker_from_id(chars.result[char]['corp']['id'])
                eve_char.alliance_id = chars.result[char]['alliance']['id']
                eve_char.alliance_name = chars.result[char]['alliance']['name']
                eve_char.save()


    @staticmethod
    def create_api_keypair(api_id, api_key, user_id):
        if not EveApiKeyPair.objects.filter(api_id=api_id).exists():
            api_pair = EveApiKeyPair()
            api_pair.api_id = api_id
            api_pair.api_key = api_key
            api_pair.user = user_id
            api_pair.save()

    @staticmethod
    def get_api_key_pairs(user):
        if EveApiKeyPair.objects.filter(user=user).exists():
            return EveApiKeyPair.objects.filter(user=user)

    @staticmethod
    def delete_api_key_pair(api_id, user_id):
        if EveApiKeyPair.objects.filter(api_id=api_id).exists():
            # Check that its owned by our user_id
            apikeypair = EveApiKeyPair.objects.get(api_id=api_id)
            if apikeypair.user.id == user_id:
                apikeypair.delete()

    @staticmethod
    def delete_characters_by_api_id(api_id, user_id):
        if EveCharacter.objects.filter(api_id=api_id).exists():
            # Check that its owned by our user_id
            characters = EveCharacter.objects.filter(api_id=api_id)

            for char in characters:
                if char.user.id == user_id:
                    char.delete()

    @staticmethod
    def check_if_character_exist(char_name):
        return EveCharacter.objects.filter(character_name=char_name).exists()

    @staticmethod
    def get_characters_by_owner_id(user):
        if EveCharacter.objects.filter(user=user).exists():
            return EveCharacter.objects.all().filter(user=user)

        return None

    @staticmethod
    def get_character_by_character_name(char_name):
        if EveCharacter.objects.filter(character_name=char_name).exists():
            return EveCharacter.objects.get(character_name=char_name)

    @staticmethod
    def get_character_by_id(char_id):
        if EveCharacter.objects.filter(character_id=char_id).exists():
            return EveCharacter.objects.get(character_id=char_id)
        
        return None

    @staticmethod
    def get_charater_alliance_id_by_id(char_id):
        if EveCharacter.objects.filter(character_id=char_id).exists():
            return EveCharacter.objects.get(character_id=char_id).alliance_id

    @staticmethod
    def check_if_character_owned_by_user(char_id, user):
        character = EveCharacter.objects.get(character_id=char_id)

        if character.user.id == user.id:
            return True
        
        return False