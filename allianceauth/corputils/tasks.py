from celery import shared_task
from allianceauth.corputils.models import CorpStats


@shared_task
def update_corpstats(pk):
    cs = CorpStats.objects.get(pk=pk)
    cs.update()


@shared_task
def update_all_corpstats():
    for cs in CorpStats.objects.all():
        update_corpstats.delay(cs.pk)
