from __future__ import unicode_literals
import requests
import json


class EveWhoManager:
    def __init__(self):
        pass

    @staticmethod
    def get_corporation_members(corpid):
        url = "http://evewho.com/api.php?type=corplist&id=%s" % corpid
        jsondata = requests.get(url).content
        data = json.loads(jsondata.decode())

        members = {}
        page_count = 0
        while len(data["characters"]):
            for row in data["characters"]:
                members[int(row["character_id"])] = {"name": row["name"], "id": int(row["character_id"])}
            page_count += 1
            jsondata = requests.get(url + "&page=%i" % page_count).content
            data = json.loads(jsondata.decode())

        return members
