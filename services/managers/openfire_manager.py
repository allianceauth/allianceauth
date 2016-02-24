import os
from urlparse import urlparse

import xmpp
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
import threading
from ofrestapi.users import Users as ofUsers
from ofrestapi import exception

import logging

logger = logging.getLogger(__name__)

class OpenfireManager:
    def __init__(self):
        pass

    @staticmethod
    def send_broadcast_threaded(group_name, broadcast_message):
        logger.debug("Starting broadcast to %s with message %s" % (group_name, broadcast_message))
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
        logger.debug("Adding username %s to openfire." % username)
        try:
            sanatized_username = OpenfireManager.__santatize_username(username)
            password = OpenfireManager.__generate_random_pass()
            api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.add_user(sanatized_username, password)
            logger.info("Added openfire user %s" % username)
        except exception.UserAlreadyExistsException:
            # User exist
            logger.error("Attempting to add a user %s to openfire which already exists on server." % username)
            return "", ""

        return sanatized_username, password

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting user %s from openfire." % username)
        try:
            api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.delete_user(username)
            logger.info("Deleted user %s from openfire." % username)
            return True
        except exception.UserNotFoundException:
            logger.error("Attempting to delete a user %s from openfire which was not found on server." % username)
            return False

    @staticmethod
    def lock_user(username):
        logger.debug("Locking openfire user %s" % username)
        api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.lock_user(username)
        logger.info("Locked openfire user %s" % username)

    @staticmethod
    def unlock_user(username):
        logger.debug("Unlocking openfire user %s" % username)
        api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.unlock_user(username)
        logger.info("Unlocked openfire user %s" % username)

    @staticmethod
    def update_user_pass(username, password=None):
        logger.debug("Updating openfire user %s password." % username)
        try:
            if not password:
                password = OpenfireManager.__generate_random_pass()
            api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.update_user(username, password=password)
            logger.info("Updated openfire user %s password." % username)
            return password
        except exception.UserNotFoundException:
            logger.error("Unable to update openfire user %s password - user not found on server." % username)
            return ""

    @staticmethod
    def update_user_groups(username, password, groups):
        logger.debug("Updating openfire user %s groups %s" % (username, groups))
        api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        response = api.get_user_groups(username)
        remote_groups = []
        if response:
            remote_groups = response['groupname']
            if isinstance(remote_groups, basestring):
                remote_groups = [remote_groups]
        logger.debug("Openfire user %s has groups %s" % (username, remote_groups))
        add_groups = []
        del_groups = []
        for g in groups:
            if not g in remote_groups:
                add_groups.append(g)
        for g in remote_groups:
            if not g in groups:
                del_groups.append(g)
        logger.info("Updating openfire groups for user %s - adding %s, removing %s" % (username, add_groups, del_groups))
        if add_groups:
            api.add_user_groups(username, add_groups)
        if del_groups:
            api.delete_user_groups(username, del_groups)
        
    @staticmethod
    def delete_user_groups(username, groups):
        logger.debug("Deleting openfire groups %s from user %s" % (groups, username))
        api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.delete_user_groups(username, groups)
        logger.info("Deleted groups %s from openfire user %s" % (groups, username))

    @staticmethod
    def send_broadcast_message(group_name, broadcast_message):
        logger.debug("Sending jabber ping to group %s with message %s" % (group_name, broadcast_message))
        # create to address
        client = xmpp.Client(settings.JABBER_URL)
        client.connect(server=(settings.JABBER_SERVER, settings.JABBER_PORT))
        client.auth(settings.BROADCAST_USER, settings.BROADCAST_USER_PASSWORD, 'broadcast')

        to_address = group_name + '@' + settings.BROADCAST_SERVICE_NAME + '.' + settings.JABBER_URL
        logger.debug("Determined ping to address: %s" % to_address)
        message = xmpp.Message(to_address, broadcast_message)
        message.setAttr('type', 'chat')
        client.send(message)
        client.Process(1)

        client.disconnect()
        logger.info("Sent jabber ping to group %s" % group_name)

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
