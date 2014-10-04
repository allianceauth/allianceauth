import evelink.api  # Raw API access
import evelink.char # Wrapped API access for the /char/ API path
import evelink.eve  # Wrapped API access for the /eve/ API path

from models import EveCharacter

class EveCharacterManager():
    
    def __init__(self):
        pass
    
    def create_character(self,character_id, character_name,corporation_id,
                         corporation_name,  alliance_id,
                         alliance_name, allianceuser_owner):
        
        eve_char = EveCharacter();
        eve_char.character_id = character_id
        eve_char.character_name = character_name
        eve_char.corporation_id = corporation_id
        eve_char.corporation_name = corporation_name
        eve_char.alliance_id = alliance_id
        eve_char.alliance_name = alliance_name
        eve_char.allianceuser_owner = allianceuser_owner
        
        eve_char.save()
    
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
        
class EveApiManager():
    
    characterManager = EveCharacterManager()
    
    def __init__(self):
        pass
    
    def CreateCharactersFromID(self,api_id, api_key, user):
        # Create user
        api = evelink.api.API(api_key=(api_id, api_key))
        # Should get characters
        account = evelink.account.Account(api=api)
        chars = account.characters()
        
        # Have our characters now lets populate database
        for char in chars.result:
            self.characterManager.create_character( chars.result[char]['id'], chars.result[char]['name'],
                                              chars.result[char]['corp']['id'], chars.result[char]['corp']['name'],
                                              chars.result[char]['alliance']['id'],chars.result[char]['alliance']['name'],
                                              user)
        #Done

    def GetCorpNameByKey(self, api_id, api_key):
        pass
    
    def GetAllianceNameByKey(self, api_id, api_key):
        pass
    
    def GetCharactersByKey(self, api_id, api_key):
        pass
    