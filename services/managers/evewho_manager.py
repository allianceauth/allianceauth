from django.conf import settings

import logging
import requests
import requests_cache
import json

requests_cache.install_cache("{}/evewho".format(settings.EVEWHO_CACHE_DIR), backend="sqlite", expire_after=3600)

class EveWhoManager():
    def __init__(self):
        pass

    @staticmethod
    def get_corporation_members(corpid):
        url = "http://evewho.com/api.php?type=corplist&id=%s" % corpid
        jsondata = requests.get(url).content
        data=json.loads(jsondata.decode())

        return {row["character_id"]:{"name":row["name"], "id":row["character_id"]} for row in data["characters"]}
