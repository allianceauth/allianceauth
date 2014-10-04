import evelink.api  # Raw API access
import evelink.char # Wrapped API access for the /char/ API path
import evelink.eve  # Wrapped API access for the /eve/ API path

api_id = '3730269'
api_key = 'BkoREwPBo4QQOGGZXcuOfXMMfSDuTttmoqtQSjiaCoYECqrPozBp4bKjYZ2XmOHL'
# Create user
api = evelink.api.API(api_key=(api_id, api_key))
account = evelink.account.Account(api=api)
chars = account.characters()
for char in chars.result:
    print char['alliance']['id']
    print char['alliance']['name']
    print char['corp']['id']
    print char['corp']['name']
    print char['id']
    print char['name']
