from corputils.models import CorpStats
from celery.task import task, periodic_task
from celery.task.schedules import crontab


@task
def update_corpstats(pk):
    cs = CorpStats.objects.get(pk=pk)
    cs.update()


@periodic_task(run_every=crontab(minute=0, hour="*/6"))
def update_all_corpstats():
    for cs in CorpStats.objects.all():
        update_corpstats.delay(cs.pk)
