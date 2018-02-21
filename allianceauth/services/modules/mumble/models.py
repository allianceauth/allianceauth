import random
import string
from passlib.hash import bcrypt_sha256

from django.db import models
from django.contrib.auth.models import Group
from allianceauth.services.hooks import NameFormatter
from allianceauth.services.abstract import AbstractServiceModel
import logging

logger = logging.getLogger(__name__)


class MumbleManager(models.Manager):
    HASH_FN = 'bcrypt-sha256'

    @staticmethod
    def get_username(user):
        from .auth_hooks import MumbleService
        return NameFormatter(MumbleService(), user).format_name()

    @staticmethod
    def sanitise_username(username):
        return username.replace(" ", "_")

    @staticmethod
    def generate_random_pass():
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

    @staticmethod
    def gen_pwhash(password):
        return bcrypt_sha256.encrypt(password.encode('utf-8'))

    def create(self, user):
        username = self.get_username(user)
        logger.debug("Creating mumble user with username {}".format(username))
        username_clean = self.sanitise_username(username)
        password = self.generate_random_pass()
        pwhash = self.gen_pwhash(password)
        logger.debug("Proceeding with mumble user creation: clean username {}, pwhash starts with {}".format(
            username_clean, pwhash[0:5]))
        logger.info("Creating mumble user {}".format(username_clean))

        result = super(MumbleManager, self).create(user=user, username=username_clean,
                                                   pwhash=pwhash, hashfn=self.HASH_FN)
        result.update_groups()
        result.credentials.update({'username': result.username, 'password': password})
        return result

    def user_exists(self, username):
        return self.filter(username=username).exists()


class MumbleUser(AbstractServiceModel):
    username = models.CharField(max_length=254, unique=True)
    pwhash = models.CharField(max_length=80)
    hashfn = models.CharField(max_length=20, default='sha1')
    groups = models.TextField(blank=True, null=True)

    objects = MumbleManager()

    def __str__(self):
        return self.username

    def update_password(self, password=None):
        init_password = password
        logger.debug("Updating mumble user %s password.".format(self.user))
        if not password:
            password = MumbleManager.generate_random_pass()
        pwhash = MumbleManager.gen_pwhash(password)
        logger.debug("Proceeding with mumble user {} password update - pwhash starts with {}".format(
            self.user, pwhash[0:5]))
        self.pwhash = pwhash
        self.hashfn = MumbleManager.HASH_FN
        self.save()
        if init_password is None:
            self.credentials.update({'username': self.username, 'password': password})

    def reset_password(self):
        self.update_password()

    def update_groups(self, groups: Group=None):
        if groups is None:
            groups = self.user.groups.all()
        groups_str = [self.user.profile.state.name]
        for group in groups:
            groups_str.append(str(group.name))
        safe_groups = ','.join(set([g.replace(' ', '-') for g in groups_str]))
        logger.info("Updating mumble user {} groups to {}".format(self.user, safe_groups))
        self.groups = safe_groups
        self.save()
        return True

    class Meta:
        permissions = (
            ("access_mumble", u"Can access the Mumble service"),
        )
