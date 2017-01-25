from __future__ import unicode_literals
import random
import string
import hashlib

from django.core.exceptions import ObjectDoesNotExist

from .models import MumbleUser

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
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def __generate_username(username, corp_ticker):
        return "[" + corp_ticker + "]" + username

    @staticmethod
    def __generate_username_blue(username, corp_ticker):
        return "[BLUE][" + corp_ticker + "]" + username

    @staticmethod
    def _gen_pwhash(password):
        return hashlib.sha1(password.encode('utf-8')).hexdigest()

    @staticmethod
    def create_user(user, corp_ticker, username, blue=False):
        logger.debug("Creating%s mumble user with username %s and ticker %s" % (' blue' if blue else '',
                                                                                username, corp_ticker))
        username_clean = MumbleManager.__santatize_username(
            MumbleManager.__generate_username_blue(username, corp_ticker) if blue else
            MumbleManager.__generate_username(username, corp_ticker))
        password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username %s, pwhash starts with %s" % (
            username_clean, pwhash[0:5]))
        if not MumbleUser.objects.filter(username=username_clean).exists():
            logger.info("Creating mumble user %s" % username_clean)
            MumbleUser.objects.create(user=user, username=username_clean, pwhash=pwhash)
            return username_clean, password
        else:
            logger.warn("Mumble user %s already exists.")
            return False

    @staticmethod
    def delete_user(user):
        logger.debug("Deleting user %s from mumble." % user)
        if MumbleUser.objects.filter(user=user).exists():
            MumbleUser.objects.filter(user=user).delete()
            logger.info("Deleted user %s from mumble" % user)
            return True
        logger.error("Unable to delete user %s from mumble: MumbleUser model not found" % user)
        return False

    @staticmethod
    def update_user_password(user, password=None):
        logger.debug("Updating mumble user %s password." % user)
        if not password:
            password = MumbleManager.__generate_random_pass()
        pwhash = MumbleManager._gen_pwhash(password)
        logger.debug("Proceeding with mumble user %s password update - pwhash starts with %s" % (user, pwhash[0:5]))
        try:
            model = MumbleUser.objects.get(user=user)
            model.pwhash = pwhash
            model.save()
            return password
        except ObjectDoesNotExist:
            logger.error("User %s not found on mumble. Unable to update password." % user)
            return False

    @staticmethod
    def update_groups(user, groups):
        logger.debug("Updating mumble user %s groups %s" % (user, groups))
        safe_groups = list(set([g.replace(' ', '-') for g in groups]))
        groups = ''
        for g in safe_groups:
            groups = groups + g + ','
        groups = groups.strip(',')
        if MumbleUser.objects.filter(user=user).exists():
            logger.info("Updating mumble user %s groups to %s" % (user, safe_groups))
            model = MumbleUser.objects.get(user=user)
            model.groups = groups
            model.save()
            return True
        else:
            logger.error("User %s not found on mumble. Unable to update groups." % user)
            return False

    @staticmethod
    def user_exists(username):
        return MumbleUser.objects.filter(username=username).exists()
