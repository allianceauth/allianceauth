from django.conf import settings


import json
import urllib2
import logging


logger = logging.getLogger(__name__)

class srpManager():
    @staticmethod
    def get_kill_id (killboard_link):
        str = (killboard_link)
        set = '0123456789'
        kill_id = ''.join([c for c in str if c in set])
        return kill_id

    @staticmethod
    def get_kill_data (kill_id):
        url = ("https://www.zkillboard.com/api/killID/%s" % kill_id)
        request = urllib2.Request(url)
        request.add_header('User-Agent',"%s Alliance Auth" % settings.DOMAIN)
        request.add_header('Content-Type','application/json')
        response = urllib2.urlopen(request)
        result = json.load(response)[0]
        if result:
            ship_type = result['victim']['shipTypeID']
            logger.debug("Ship type for kill ID %s is determined to be %s" % (kill_id, ship_type))
            ship_value = result['zkb']['totalValue']
            logger.debug("total loss value for kill id %s is %s" %(kill_id, ship_value))
            return (ship_type, ship_value)
        else:
            raise ValueError("Invalid Kill ID")

    @staticmethod
    def get_ship_name (ship_type):
        url = ("https://jetbalsa.com/api/json.php/invTypes/%s" % ship_type)
        request = urllib2.Request(url)
        request.add_header('User-Agent',"%s Alliance Auth" % settings.DOMAIN)
        request.add_header('Content-Type','application/json')
        response = urllib2.urlopen(request)
        result = json.load(response)
        if result:
            ship_name = result['typeName']
            logger.debug("ship type %s determined to be %s" % (ship_type, ship_name))
            return ship_name
        else:
            logger.debug("ship type %s is invalid" % ship_type)
            raise ValueError("Cannot get ship name")










