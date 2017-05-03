from corputils.models import CorpStats
from alliance_auth.celeryapp import app


@app.task
def update_corpstats(pk):
    cs = CorpStats.objects.get(pk=pk)
    cs.update()


@app.task
def update_all_corpstats():
    for cs in CorpStats.objects.all():
        update_corpstats.delay(cs.pk)
