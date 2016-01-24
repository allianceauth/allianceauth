
from django.conf import settings

import logging
import requests
import json


class EveWhoManager():
    def __init__(self):
        pass

    @staticmethod
    def get_corporation_members(corpid):
        url = "http://evewho.com/api.php?type=corplist&id=%s" % corpid
        jsondata = requests.get(url).content
        data=json.loads(jsondata.decode())

        return {row["character_id"]:{"name":row["name"], "id":row["character_id"]} for row in data["characters"]}
