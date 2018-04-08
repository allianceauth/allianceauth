import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from allianceauth.notifications import notify
from celery import shared_task
from requests.exceptions import HTTPError
from allianceauth.services.hooks import NameFormatter
from .manager import DiscordOAuthManager, DiscordApiBackoff
from .models import DiscordUser
from allianceauth.services.tasks import QueueOnce

logger = logging.getLogger(__name__)


class DiscordTasks:
    def __init__(self):
        pass

    @classmethod
    def add_user(cls, user, code):
        groups = DiscordTasks.get_groups(user)
        nickname = None
        if settings.DISCORD_SYNC_NAMES:
            nickname = DiscordTasks.get_nickname(user)
        user_id = DiscordOAuthManager.add_user(code, groups, nickname=nickname)
        if user_id:
            discord_user = DiscordUser()
            discord_user.user = user
            discord_user.uid = user_id
            discord_user.save()
            return True
        return False

    @classmethod
    def delete_user(cls, user, notify_user=False):
        if cls.has_account(user):
            logger.debug("User %s has discord account %s. Deleting." % (user, user.discord.uid))
            if DiscordOAuthManager.delete_user(user.discord.uid):
                user.discord.delete()
                if notify_user:
                    notify(user, 'Discord Account Disabled', level='danger')
                return True
        return False

    @classmethod
    def has_account(cls, user):
        """
        Check if the user has an account (has a DiscordUser record)
        :param user: django.contrib.auth.models.User
        :return: bool
        """
        try:
            user.discord
        except ObjectDoesNotExist:
            return False
        else:
            return True

    @staticmethod
    @shared_task(bind=True, name='discord.update_groups', base=QueueOnce)
    def update_groups(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating discord groups for user %s" % user)
        if DiscordTasks.has_account(user):
            groups = DiscordTasks.get_groups(user)
            logger.debug("Updating user %s discord groups to %s" % (user, groups))
            try:
                DiscordOAuthManager.update_groups(user.discord.uid, groups)
            except DiscordApiBackoff as bo:
                logger.info("Discord group sync API back off for %s, "
                            "retrying in %s seconds" % (user, bo.retry_after_seconds))
                raise self.retry(countdown=bo.retry_after_seconds)
            except HTTPError as e:
                if e.response.status_code == 404:
                    try:
                        if e.response.json()['code'] == 10007:
                            # user has left the server
                            DiscordTasks.delete_user(user)
                            return
                    finally:
                        raise e
            except Exception as e:
                if self:
                    logger.exception("Discord group sync failed for %s, retrying in 10 mins" % user)
                    raise self.retry(countdown=60 * 10)
                else:
                    # Rethrow
                    raise e
            logger.debug("Updated user %s discord groups." % user)
        else:
            logger.debug("User does not have a discord account, skipping")

    @staticmethod
    @shared_task(name='discord.update_all_groups')
    def update_all_groups():
        logger.debug("Updating ALL discord groups")
        for discord_user in DiscordUser.objects.exclude(uid__exact=''):
            DiscordTasks.update_groups.delay(discord_user.user.pk)

    @staticmethod
    @shared_task(bind=True, name='discord.update_nickname', base=QueueOnce)
    def update_nickname(self, pk):
        user = User.objects.get(pk=pk)
        logger.debug("Updating discord nickname for user %s" % user)
        if DiscordTasks.has_account(user):
            if user.profile.main_character:
                character = user.profile.main_character
                logger.debug("Updating user %s discord nickname to %s" % (user, character.character_name))
                try:
                    DiscordOAuthManager.update_nickname(user.discord.uid, DiscordTasks.get_nickname(user))
                except DiscordApiBackoff as bo:
                    logger.info("Discord nickname update API back off for %s, "
                                "retrying in %s seconds" % (user, bo.retry_after_seconds))
                    raise self.retry(countdown=bo.retry_after_seconds)
                except Exception as e:
                    if self:
                        logger.exception("Discord nickname sync failed for %s, retrying in 10 mins" % user)
                        raise self.retry(countdown=60 * 10)
                    else:
                        # Rethrow
                        raise e
                logger.debug("Updated user %s discord nickname." % user)
            else:
                logger.debug("User %s does not have a main character" % user)
        else:
            logger.debug("User %s does not have a discord account" % user)

    @staticmethod
    @shared_task(name='discord.update_all_nicknames')
    def update_all_nicknames():
        logger.debug("Updating ALL discord nicknames")
        for discord_user in DiscordUser.objects.exclude(uid__exact=''):
            DiscordTasks.update_nickname.delay(discord_user.user.pk)

    @classmethod
    def disable(cls):
        DiscordUser.objects.all().delete()

    @staticmethod
    def get_nickname(user):
        from .auth_hooks import DiscordService
        return NameFormatter(DiscordService(), user).format_name()

    @staticmethod
    def get_groups(user):
        return [g.name for g in user.groups.all()] + [user.profile.state.name]
