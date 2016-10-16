from __future__ import unicode_literals
from django.conf import settings
from datetime import datetime

import logging
import requests
import json

logger = logging.getLogger(__name__)

appkey = settings.FLEETUP_APP_KEY
userid = settings.FLEETUP_USER_ID
apiid = settings.FLEETUP_API_ID
groupid = settings.FLEETUP_GROUP_ID


class FleetUpManager:
    def __init__(self):
        pass

    @staticmethod
    def get_fleetup_members():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/GroupCharacters/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
            fmembers = json.loads(jsondata.decode())
            return {row["UserId"]: {"user_id": row["UserId"],
                                    "char_name": row["EveCharName"],
                                    "char_id": row["EveCharId"],
                                    "corporation": row["Corporation"]} for row in fmembers["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.debug("No fleetup members retrieved.")
        return {}

    @staticmethod
    def get_fleetup_operations():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Operations/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
            foperations = json.loads(jsondata.decode())
            return {row["StartString"]: {"subject": row["Subject"],
                                         "start": (datetime.strptime(row["StartString"], "%Y-%m-%d %H:%M:%S")),
                                         "end": (datetime.strptime(row["EndString"], "%Y-%m-%d %H:%M:%S")),
                                         "operation_id": row["OperationId"],
                                         "location": row["Location"],
                                         "location_info": row["LocationInfo"],
                                         "details": row["Details"],
                                         "url": row["Url"],
                                         "doctrine": row["Doctrines"],
                                         "organizer": row["Organizer"]} for row in foperations["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.debug("No fleetup operations retrieved.")
        return {}

    @staticmethod
    def get_fleetup_timers():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Timers/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
            ftimers = json.loads(jsondata.decode())
            return {row["ExpiresString"]: {"solarsystem": row["SolarSystem"],
                                           "planet": row["Planet"],
                                           "moon": row["Moon"],
                                           "owner": row["Owner"],
                                           "type": row["Type"],
                                           "timer_type": row["TimerType"],
                                           "expires": (datetime.strptime(row["ExpiresString"], "%Y-%m-%d %H:%M:%S")),
                                           "notes": row["Notes"]} for row in ftimers["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.debug("No fleetup timers retrieved.")
        return {}

    @staticmethod
    def get_fleetup_doctrines():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Doctrines/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
            fdoctrines = json.loads(jsondata.decode())
            return {"fleetup_doctrines": fdoctrines["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.debug("No fleetup doctrines retrieved.")
        return {"fleetup_doctrines": []}

    @staticmethod
    def get_fleetup_doctrine(doctrinenumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/DoctrineFittings/%s" % doctrinenumber
        try:
            jsondata = requests.get(url).content
            fdoctrine = json.loads(jsondata.decode())
            return {"fitting_doctrine": fdoctrine}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.warn("Fleetup doctrine number %s not found" % doctrinenumber)
        return {"fitting_doctrine": {}}

    @staticmethod
    def get_fleetup_fittings():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Fittings/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
            ffittings = json.loads(jsondata.decode())
            return {row["FittingId"]: {"fitting_id": row["FittingId"],
                                       "name": row["Name"],
                                       "icon_id": row["EveTypeId"],
                                       "hull": row["HullType"],
                                       "shiptype": row["ShipType"],
                                       "estimated": row["EstPrice"],
                                       "faction": row["Faction"],
                                       "categories": row["Categories"],
                                       "last_update": (
                                       datetime.strptime(row["LastUpdatedString"], "%Y-%m-%d %H:%M:%S"))} for row in
                    ffittings["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.debug("No fleetup fittings retrieved.")
        return {}

    @staticmethod
    def get_fleetup_fitting(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Fitting/%s" % fittingnumber
        try:
            jsondata = requests.get(url).content
            ffitting = json.loads(jsondata.decode())
            return {"fitting_data": ffitting["Data"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.warn("Fleetup fitting number %s not found" % fittingnumber)
        except KeyError:
            logger.warn("Failed to retrieve fleetup fitting number %s" % fittingnumber)
        return {"fitting_data": {}}

    @staticmethod
    def get_fleetup_doctrineid(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Fitting/%s" % fittingnumber
        try:
            jsondata = requests.get(url).content
            fdoctrineid = json.loads(jsondata.decode())
            return fdoctrineid['Data']['Doctrines'][0]['DoctrineId']
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.warn("Fleetup doctrine number not found for fitting number %s" % fittingnumber)
        except (KeyError, IndexError):
            logger.debug("Fleetup fitting number %s not in a doctrine." % fittingnumber)
        return None

    @staticmethod
    def get_fleetup_fitting_eft(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(
            apiid) + "/Fitting/%s/eft" % fittingnumber
        try:
            jsondata = requests.get(url).content
            ffittingeft = json.loads(jsondata.decode())
            return {"fitting_eft": ffittingeft["Data"]["FittingData"]}
        except requests.exceptions.ConnectionError:
            logger.warn("Can't connect to Fleet-Up API, is it offline?!")
        except (ValueError, UnicodeDecodeError):
            logger.warn("Fleetup fitting eft not found for fitting number %s" % fittingnumber)
        return {"fitting_eft": {}}
