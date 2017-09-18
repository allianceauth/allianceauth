from django.db import models
import logging

logger = logging.getLogger(__name__)


class CorpStatsQuerySet(models.QuerySet):
    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            logger.debug('Returning all corpstats for superuser %s.' % user)
            return self

        try:
            char = user.profile.main_character
            assert char
            # build all accepted queries
            queries = [models.Q(token__user=user)]
            if user.has_perm('corputils.view_corp_corpstats'):
                queries.append(models.Q(corp__corporation_id=char.corporation_id))
            if user.has_perm('corputils.view_alliance_corpstats'):
                queries.append(models.Q(corp__alliance__alliance_id=char.alliance_id))
            if user.has_perm('corputils.view_state_corpstats'):
                queries.append(models.Q(corp__in=user.profile.state.member_corporations.all()))
                queries.append(models.Q(corp__alliance__in=user.profile.state.member_alliances.all()))
            logger.debug('%s queries for user %s visible corpstats.' % (len(queries), user))
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return self.filter(query)
        except AssertionError:
            logger.debug('User %s has no main character. No corpstats visible.' % user)
            return self.none()        


class CorpStatsManager(models.Manager):
    def get_queryset(self):
        return CorpStatsQuerySet(self.model, using=self._db)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
