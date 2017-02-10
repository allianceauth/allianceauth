from __future__ import unicode_literals
from django.utils import six
import re
import random
import string
try:
    from urlparse import urlparse
except ImportError:
    # python 3
    from urllib.parse import urlparse

import sleekxmpp
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
    def __sanitize_username(username):
        # https://xmpp.org/extensions/xep-0106.html#escaping
        replace = [
            ("\\", "\\5c"),  # Escape backslashes first to double escape existing escape sequences
            ("\"", "\\22"),
            ("&", "\\26"),
            ("'", "\\27"),
            ("/", "\\2f"),
            (":", "\\3a"),
            ("<", "\\3c"),
            (">", "\\3e"),
            ("@", "\\40"),
            ("\u007F", ""),
            ("\uFFFE", ""),
            ("\uFFFF", ""),
            (" ", "\\20"),
        ]

        sanitized = username.strip(' ')

        for find, rep in replace:
            sanitized = sanitized.replace(find, rep)

        return sanitized

    @staticmethod
    def __generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def _sanitize_groupname(name):
        name = name.strip(' _')
        return re.sub('[^\w.-]', '', name)

    @staticmethod
    def add_user(username):
        logger.debug("Adding username %s to openfire." % username)
        try:
            sanitized_username = OpenfireManager.__sanitize_username(username)
            password = OpenfireManager.__generate_random_pass()
            api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.add_user(sanitized_username, password)
            logger.info("Added openfire user %s" % username)
        except exception.UserAlreadyExistsException:
            # User exist
            logger.error("Attempting to add a user %s to openfire which already exists on server." % username)
            return "", ""

        return sanitized_username, password

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
    def update_user_groups(username, groups):
        logger.debug("Updating openfire user %s groups %s" % (username, groups))
        api = ofUsers(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        response = api.get_user_groups(username)
        remote_groups = []
        if response:
            remote_groups = response['groupname']
            if isinstance(remote_groups, six.string_types):
                remote_groups = [remote_groups]
        logger.debug("Openfire user %s has groups %s" % (username, remote_groups))
        add_groups = []
        del_groups = []
        for g in groups:
            g = OpenfireManager._sanitize_groupname(g)
            if g not in remote_groups:
                add_groups.append(g)
        for g in remote_groups:
            g = OpenfireManager._sanitize_groupname(g)
            if g not in groups:
                del_groups.append(g)
        logger.info(
            "Updating openfire groups for user %s - adding %s, removing %s" % (username, add_groups, del_groups))
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
        to_address = group_name + '@' + settings.BROADCAST_SERVICE_NAME + '.' + settings.JABBER_URL
        xmpp = PingBot(settings.BROADCAST_USER, settings.BROADCAST_USER_PASSWORD, to_address, broadcast_message)
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0199')  # XMPP Ping
        if xmpp.connect():
            xmpp.process(block=True)
            logger.info("Sent jabber ping to group %s" % group_name)
        else:
            raise ValueError("Unable to connect to jabber server.")


class PingBot(sleekxmpp.ClientXMPP):
    """
    A copy-paste of the example client bot from
    http://sleekxmpp.com/getting_started/sendlogout.html
    """
    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        self.recipient = recipient
        self.msg = message

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)


class XmppThread(threading.Thread):
    def __init__(self, thread_id, name, counter, group, message, ):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.group = group
        self.message = message

    def run(self):
        OpenfireManager.send_broadcast_message(self.group, self.message)
