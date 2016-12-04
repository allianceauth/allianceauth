from django.contrib.auth.models import Group
from django.conf import settings

class GroupManager:
    def __init__(self):
        pass

    @staticmethod
    def get_joinable_groups():
        return Group.objects.exclude(authgroup__internal=True)

    @staticmethod
    def joinable_group(group):
        """
        Check if a group is a user joinable group, i.e.
        not an internal group for Corp, Alliance, Members etc
        :param group: django.contrib.auth.models.Group object
        :return: bool True if its joinable, False otherwise
        """
        return not group.authgroup.internal
