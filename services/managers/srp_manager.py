from __future__ import unicode_literals
from django.conf import settings

import requests
import logging

logger = logging.getLogger(__name__)


class srpManager:
    def __init__(self):
        pass

    @staticmethod
    def get_kill_id(killboard_link):
        num_set = '0123456789'
        kill_id = ''.join([c for c in killboard_link if c in num_set])
        return kill_id

    @staticmethod
    def get_kill_data(kill_id):
        url = ("https://www.zkillboard.com/api/killID/%s" % kill_id)
        headers = {
            'User-Agent': "%s Alliance Auth" % settings.DOMAIN,
            'Content-Type': 'application/json',
        }
        r = requests.get(url, headers=headers)
        result = r.json()[0]
        if result:
            ship_type = result['victim']['shipTypeID']
            logger.debug("Ship type for kill ID %s is determined to be %s" % (kill_id, ship_type))
            ship_value = result['zkb']['totalValue']
            logger.debug("total loss value for kill id %s is %s" % (kill_id, ship_value))
            return ship_type, ship_value
        else:
            raise ValueError("Invalid Kill ID")

    @staticmethod
    def get_ship_name(ship_type):
        url = ("https://jetbalsa.com/api/json.php/invTypes/%s" % ship_type)
        headers = {
            'User-Agent': "%s Alliance Auth" % settings.DOMAIN,
            'Content-Type': 'application/json',
        }
        r = requests.get(url, headers=headers)
        result = r.json()
        if result:
            ship_name = result['typeName']
            logger.debug("ship type %s determined to be %s" % (ship_type, ship_name))
            return ship_name
        else:
            logger.debug("ship type %s is invalid" % ship_type)
            raise ValueError("Cannot get ship name")
