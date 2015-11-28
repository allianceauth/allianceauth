import os
from urlparse import urlparse

import xmpp
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from openfire import exception
from openfire import UserService

from authentication.managers import AuthServicesInfoManager

import threading


class OpenfireManager:
    def __init__(self):
        pass

    @staticmethod
    def send_broadcast_threaded(group_name, broadcast_message):
        broadcast_thread = XmppThread(1, "XMPP Broadcast Thread", 1, group_name, broadcast_message)
        broadcast_thread.start()

    @staticmethod
    def __add_address_to_username(username):
        address = urlparse(settings.OPENFIRE_ADDRESS).netloc.split(":")[0]
        completed_username = username + "@" + address
        return completed_username

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def add_user(username):

        try:
            sanatized_username = OpenfireManager.__santatize_username(username)
            password = OpenfireManager.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.add_user(sanatized_username, password)

        except exception.UserAlreadyExistsException:
            # User exist
            return "", ""

        return sanatized_username, password

    @staticmethod
    def delete_user(username):
        try:
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.delete_user(username)
            return True
        except exception.UserNotFoundException:
            return False

    @staticmethod
    def lock_user(username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.lock_user(username)

    @staticmethod
    def unlock_user(username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.unlock_user(username)

    @staticmethod
    def update_user_pass(username):
        try:
            password = OpenfireManager.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.update_user(username, password)
            return password
        except exception.UserNotFoundException:
            return ""

    @staticmethod
    def update_user_groups(username, password, groups):
        try:
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.update_user(username, password, "", "", groups)
        except exception.HTTPException as e:
            print e

    @staticmethod
    def delete_user_groups(username, groups):

        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.delete_group(username, groups)

    @staticmethod
    def send_broadcast_message(group_name, broadcast_message):
        # create to address
        client = xmpp.Client(settings.JABBER_URL)
        client.connect(server=(settings.JABBER_SERVER, settings.JABBER_PORT))
        client.auth(settings.BROADCAST_USER, settings.BROADCAST_USER_PASSWORD, 'broadcast')

        to_address = group_name + '@' + settings.BROADCAST_SERVICE_NAME + '.' + settings.JABBER_URL
        message = xmpp.Message(to_address, broadcast_message)
        message.setAttr('type', 'chat')
        client.send(message)
        client.Process(1)

        client.disconnect()

class XmppThread (threading.Thread):
    def __init__(self, threadID, name, counter, group, message,):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.group = group
        self.message = message
    def run(self):
        print "Starting " + self.name
        OpenfireManager.send_broadcast_message(self.group, self.message)
        print "Exiting " + self.name
