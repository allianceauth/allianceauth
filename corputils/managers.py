from django.db import models
from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter


class CorpStatsQuerySet(models.QuerySet):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            return self

        auth = AuthServicesInfo.objects.get(user=user)
        try:
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            # build all accepted queries
            queries = []
            if user.has_perm('corputils.view_corp_corpstats'):
                queries.append(models.Q(corp__corporation_id=char.corporation_id))
            if user.has_perm('corputils.view_alliance_corpstats'):
                queries.append(models.Q(corp__alliance__alliance_id=char.alliance_id))
            if user.has_perm('corputils.view_blue_corpstats'):
                queries.append(models.Q(corp__is_blue=True))

            # filter based on queries
            if queries:
                query = queries.pop()
                for q in queries:
                    query |= q
                return self.filter(query)
            else:
                # not allowed to see any
                return self.none()
        except EveCharacter.DoesNotExist:
            return self.none()        


class CorpStatsManager(models.Manager):
    def get_queryset(self):
        return CorpStatsQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
