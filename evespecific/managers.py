from models import EveCharacter
from services.eveapi_manager import EveApiManager


class EveCharacterManager():
    
    def __init__(self):
        pass
    
    def create_character(self, character_id, character_name, corporation_id,
                         corporation_name,  corporation_ticker, alliance_id,
                         alliance_name, allianceuser_owner):
        
        eve_char = EveCharacter();
        eve_char.character_id = character_id
        eve_char.character_name = character_name
        eve_char.corporation_id = corporation_id
        eve_char.corporation_name = corporation_name
        eve_char.corporation_ticker = corporation_ticker
        eve_char.alliance_id = alliance_id
        eve_char.alliance_name = alliance_name
        eve_char.allianceuser_owner = allianceuser_owner
        
        eve_char.save()

    def create_characters_from_list(self, chars, owner):
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
                                      owner)

    def check_if_character_exist(self, char_name):
        return EveCharacter.objects.filter(character_name=char_name).exists()

    def get_characters_by_owner_id(self, owner_id):
        return EveCharacter.objects.all().filter(allianceuser_owner=owner_id)
    
    def get_character_by_id(self, char_id):
        if EveCharacter.objects.filter(character_id = char_id).exists():
            return EveCharacter.objects.get(character_id=char_id)
        
        return None
    
    def check_if_character_owned_by_user(self, char_id, user_id):
        character = EveCharacter.objects.get(character_id = char_id)

        if character.allianceuser_owner.id == user_id:
            return True
        
        return False