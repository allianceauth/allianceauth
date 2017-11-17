from allianceauth import NAME

import requests
import logging

logger = logging.getLogger(__name__)


class SRPManager:
    def __init__(self):
        pass

    @staticmethod
    def get_kill_id(killboard_link):
        num_set = '0123456789'
        kill_id = ''.join([c for c in killboard_link if c in num_set])
        return kill_id

    @staticmethod
    def get_kill_data(kill_id):
        url = ("https://www.zkillboard.com/api/killID/%s/" % kill_id)
        headers = {
            'User-Agent': NAME,
            'Content-Type': 'application/json',
        }
        r = requests.get(url, headers=headers)
        result = r.json()[0]
        if result:
            ship_type = result['victim']['ship_type_id']
            logger.debug("Ship type for kill ID %s is %s" % (kill_id, ship_type))
            ship_value = result['zkb']['totalValue']
            logger.debug("Total loss value for kill id %s is %s" % (kill_id, ship_value))
            victim_id = result['victim']['character_id']
            return ship_type, ship_value, victim_id
        else:
            raise ValueError("Invalid Kill ID")

