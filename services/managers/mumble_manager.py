from __future__ import unicode_literals
import os
import hashlib

from services.models import MumbleUser

import logging

logger = logging.getLogger(__name__)


class MumbleManager:
    def __init__(self):
        pass

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __generate_username(username, corp_ticker):
        return "[" + corp_ticker + "]" + username

    @staticmethod
    def __generate_username_blue(username, corp_ticker):
        return "[BLUE][" + corp_ticker + "]" + username

    @staticmethod
    def _gen_pwhash(password):
        return hashlib.sha1(password).hexdigest()

    @staticmethod
    def create_user(corp_ticker, username):
        logger.debug("Creating mumble user with username %s and ticker %s" % (username, corp_ticker))
        username_clean = MumbleManager.__santatize_username(MumbleManager.__generate_username(username, corp_ticker))
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username %s, pwhash starts with %s" % (
            username_clean, pwhash[0:5]))
        if MumbleUser.objects.filter(username=username_clean).exists() is False:
            logger.info("Creating mumble user %s" % username_clean)
            MumbleUser.objects.create(username=username_clean, pwhash=pwhash)
            return username_clean, password
        else:
            logger.warn("Mumble user %s already exists. Updating password")
            model = MumbleUser.objects.get(username=username_clean)
            model.pwhash = pwhash
            model.save()
            logger.info("Updated mumble user %s" % username_clean)
            return username_clean, password

    @staticmethod
    def create_blue_user(corp_ticker, username):
        logger.debug("Creating mumble blue user with username %s and ticker %s" % (username, corp_ticker))
        username_clean = MumbleManager.__santatize_username(
            MumbleManager.__generate_username_blue(username, corp_ticker))
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username %s, pwhash starts with %s" % (
            username_clean, pwhash[0:5]))
        if MumbleUser.objects.filter(username=username_clean).exists() is False:
            logger.info("Creating mumble user %s" % username_clean)
            MumbleUser.objects.create(username=username_clean, pwhash=pwhash)
            return username_clean, password
        else:
            logger.warn("Mumble user %s already exists. Updating password")
            model = MumbleUser.objects.get(username=username_clean)
            model.pwhash = pwhash
            model.save()
            logger.info("Updated mumble user %s" % username_clean)
            return username_clean, password

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting user %s from mumble." % username)
        if MumbleUser.objects.filter(username=username).exists():
            MumbleUser.objects.filter(username=username).delete()
            logger.info("Deleted user %s from mumble" % username)
            return True
        logger.error("Unable to delete user %s from mumble: MumbleUser model not found" % username)
        return False

    @staticmethod
    def update_user_password(username, password=None):
        logger.debug("Updating mumble user %s password." % username)
        if not password:
            password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user %s password update - pwhash starts with %s" % (username, pwhash[0:5]))
        if MumbleUser.objects.filter(username=username).exists():
            model = MumbleUser.objects.get(username=username)
            model.pwhash = pwhash
            model.save()
            return password
        logger.error("User %s not found on mumble. Unable to update password." % username)
        return ""

    @staticmethod
    def update_groups(username, groups):
        logger.debug("Updating mumble user %s groups %s" % (username, groups))
        safe_groups = list(set([g.replace(' ', '-') for g in groups]))
        groups = ''
        for g in safe_groups:
            groups = groups + g + ','
        groups = groups.strip(',')
        if MumbleUser.objects.filter(username=username).exists():
            logger.info("Updating mumble user %s groups to %s" % (username, safe_groups))
            model = MumbleUser.objects.get(username=username)
            model.groups = groups
            model.save()
        else:
            logger.error("User %s not found on mumble. Unable to update groups." % username)
