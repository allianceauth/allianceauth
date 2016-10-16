from __future__ import unicode_literals

from django.contrib import admin

from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter
from services.tasks import update_jabber_groups
from services.tasks import update_mumble_groups
from services.tasks import update_forum_groups
from services.tasks import update_ipboard_groups
from services.tasks import update_smf_groups
from services.tasks import update_teamspeak3_groups
from services.tasks import update_discord_groups
from services.tasks import update_discord_nickname
from services.tasks import update_discourse_groups


@admin.register(AuthServicesInfo)
class AuthServicesInfoManager(admin.ModelAdmin):
    @staticmethod
    def main_character(obj):
        if obj.main_char_id:
            try:
                return EveCharacter.objects.get(character_id=obj.main_char_id)
            except EveCharacter.DoesNotExist:
                pass
        return None

    def sync_jabber(self, request, queryset):
        count = 0
        for a in queryset:  # queryset filtering doesn't work here?
            if a.jabber_username != "":
                update_jabber_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s jabber accounts queued for group sync." % count)

    sync_jabber.short_description = "Sync groups for selected jabber accounts"

    def sync_mumble(self, request, queryset):
        count = 0
        for a in queryset:
            if a.mumble_username != "":
                update_mumble_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s mumble accounts queued for group sync." % count)

    sync_mumble.short_description = "Sync groups for selected mumble accounts"

    def sync_forum(self, request, queryset):
        count = 0
        for a in queryset:
            if a.forum_username != "":
                update_forum_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s forum accounts queued for group sync." % count)

    sync_forum.short_description = "Sync groups for selected forum accounts"

    def sync_ipboard(self, request, queryset):
        count = 0
        for a in queryset:
            if a.ipboard_username != "":
                update_ipboard_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s ipboard accounts queued for group sync." % count)

    sync_ipboard.short_description = "Sync groups for selected ipboard accounts"

    def sync_smf(self, request, queryset):
        count = 0
        for a in queryset:
            if a.smf_username != "":
                update_smf_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s smf accounts queued for group sync." % count)

    sync_smf.short_description = "Sync groups for selected smf accounts"

    def sync_teamspeak(self, request, queryset):
        count = 0
        for a in queryset:
            if a.teamspeak3_uid != "":
                update_teamspeak3_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s teamspeak accounts queued for group sync." % count)

    sync_teamspeak.short_description = "Sync groups for selected teamspeak accounts"

    def sync_discord(self, request, queryset):
        count = 0
        for a in queryset:
            if a.discord_uid != "":
                update_discord_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s discord accounts queued for group sync." % count)

    sync_discord.short_description = "Sync groups for selected discord accounts"

    def sync_discourse(self, request, queryset):
        count = 0
        for a in queryset:
            if a.discourse_username != "":
                update_discourse_groups.delay(a.user.pk)
                count += 1
        self.message_user(request, "%s discourse accounts queued for group sync." % count)

    sync_discourse.short_description = "Sync groups for selected discourse accounts"

    def sync_nicknames(self, request, queryset):
        count = 0
        for a in queryset:
            if a.discord_uid != "":
                update_discord_nickname(a.user.pk)
                count += 1
        self.message_user(request, "%s discord accounts queued for nickname sync." % count)

    sync_nicknames.short_description = "Sync nicknames for selected discord accounts"

    actions = [
        'sync_jabber',
        'sync_mumble',
        'sync_forum',
        'sync_ipboard',
        'sync_smf',
        'sync_teamspeak',
        'sync_discord',
        'sync_discourse',
        'sync_nicknames',
    ]

    search_fields = [
        'user__username',
        'ipboard_username',
        'xenforo_username',
        'forum_username',
        'jabber_username',
        'mumble_username',
        'teamspeak3_uid',
        'discord_uid',
        'discourse_username',
        'ips4_username',
        'smf_username',
        'market_username',
        'main_char_id',
    ]
    list_display = ('user', 'main_character')
