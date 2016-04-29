from django.conf import settings
from django.http import HttpResponse
from datetime import datetime

import logging
import requests
import json

appkey = settings.FLEETUP_APP_KEY
userid = settings.FLEETUP_USER_ID
apiid = settings.FLEETUP_API_ID
groupid = settings.FLEETUP_GROUP_ID

class FleetUpManager():
    def __init__(self):
        pass

    @staticmethod
    def get_fleetup_members():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/GroupCharacters/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        fmembers=json.loads(jsondata.decode())

        return {row["UserId"]:{"user_id":row["UserId"],
                               "char_name":row["EveCharName"],
                               "char_id":row["EveCharId"],
                               "corporation":row["Corporation"]} for row in fmembers["Data"]}

    @staticmethod
    def get_fleetup_operations():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Operations/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        foperations=json.loads(jsondata.decode())

        return {row["StartString"]:{"subject":row["Subject"],
                           "start": (datetime.strptime(row["StartString"], "%Y-%m-%d %H:%M:%S")),
                           "end": (datetime.strptime(row["EndString"], "%Y-%m-%d %H:%M:%S")),
                           "operation_id":row["OperationId"],
                           "location":row["Location"],
                           "location_info":row["LocationInfo"],
                           "details":row["Details"],
                           "url":row["Url"],
                           "doctrine":row["Doctrines"],
                           "organizer":row["Organizer"]} for row in foperations["Data"]}

    @staticmethod
    def get_fleetup_timers():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Timers/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        ftimers=json.loads(jsondata.decode())

        return {row["ExpiresString"]:{"solarsystem":row["SolarSystem"],
                           "planet":row["Planet"],
                           "moon":row["Moon"],
                           "owner":row["Owner"],
                           "type":row["Type"],
                           "timer_type":row["TimerType"],
                           "expires": (datetime.strptime(row["ExpiresString"], "%Y-%m-%d %H:%M:%S")),
                           "notes":row["Notes"]} for row in ftimers["Data"]}

    @staticmethod
    def get_fleetup_doctrines():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Doctrines/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        fdoctrines=json.loads(jsondata.decode())

        return {"fleetup_doctrines":fdoctrines["Data"]}

    @staticmethod
    def get_fleetup_doctrine(doctrinenumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/DoctrineFittings/%s" % doctrinenumber
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        fdoctrine=json.loads(jsondata.decode())

        return {"fitting_doctrine":fdoctrine}

    @staticmethod
    def get_fleetup_fittings():
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Fittings/" + str(groupid) + ""
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        ffittings=json.loads(jsondata.decode())

        return {row["FittingId"]:{"fitting_id":row["FittingId"],
                               "name":row["Name"],
                               "icon_id":row["EveTypeId"],
                               "hull":row["HullType"],
                               "shiptype":row["ShipType"],
                               "estimated":row["EstPrice"],
                               "faction":row["Faction"],
                               "categories":row["Categories"],
                               "last_update":(datetime.strptime(row["LastUpdatedString"], "%Y-%m-%d %H:%M:%S"))} for row in ffittings["Data"]}

    @staticmethod
    def get_fleetup_fitting(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Fitting/%s" % fittingnumber
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        ffitting=json.loads(jsondata.decode())

        return {"fitting_data":ffitting["Data"]}

    @staticmethod
    def get_fleetup_doctrineid(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Fitting/%s" % fittingnumber
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        fdoctrineid=json.loads(jsondata.decode())

        return fdoctrineid['Data']['Doctrines'][0]['DoctrineId']

    @staticmethod
    def get_fleetup_fitting_eft(fittingnumber):
        url = "http://api.fleet-up.com/Api.svc/" + str(appkey) + "/" + str(userid) + "/" + str(apiid) + "/Fitting/%s/eft" % fittingnumber
        try:
            jsondata = requests.get(url).content
        except requests.exceptions.ConnectionError:
            return HttpResponse("Can't connect to Fleet-Up API, is it offline?!")
        ffittingeft=json.loads(jsondata.decode())

        return {"fitting_eft":ffittingeft["Data"]["FittingData"]}
