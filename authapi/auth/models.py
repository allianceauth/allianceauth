from django.contrib.auth.models import Group as AuthGroup
from groupmanagement.models import HiddenGroup, OpenGroup, GroupDescription

class Group(AuthGroup):
    class Meta:
        proxy=True

    @property
    def hidden(self):
        return HiddenGroup.objects.filter(group=self).exists()

    @hidden.setter
    def hidden(self, value):
        if value:
            HiddenGroup.objects.get_or_create(group=self)
        else:
            HiddenGroup.objects.filter(group=self).delete()

    @property
    def open(self):
        return OpenGroup.objects.filter(group=self).exists()

    @open.setter
    def open(self, value):
        if value:
            OpenGroup.objects.get_or_create(group=self)
        else:
            OpenGroup.objects.filter(group=self).delete()

    @property
    def description(self):
        try:
            return GroupDescription.objects.get(group=self).description
        except GroupDescription.DoesNotExist:
            return ''

    @description.setter
    def description(self, value):
        if value:
            GroupDescription.objects.update_or_create(group=self, defaults={'description': value})
        else:
            GroupDescription.objects.filter(group=self).delete()
