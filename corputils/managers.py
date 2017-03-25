from django.db import models


class CorpStatsQuerySet(models.QuerySet):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            return self

        try:
            assert user.profile.main_character
            char = user.profile.main_character
            # build all accepted queries
            queries = []
            if user.has_perm('corputils.view_corp_corpstats'):
                queries.append(models.Q(corp__corporation_id=char.corporation_id))
            if user.has_perm('corputils.view_alliance_corpstats'):
                queries.append(models.Q(corp__alliance__alliance_id=char.alliance_id))

            # filter based on queries
            if queries:
                query = queries.pop()
                for q in queries:
                    query |= q
                return self.filter(query)
            else:
                # not allowed to see any
                return self.none()
        except AssertionError:
            return self.none()        


class CorpStatsManager(models.Manager):
    def get_queryset(self):
        return CorpStatsQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
