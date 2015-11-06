from util import bootstrap_permissions
from celerytask.tasks import run_corp_update

bootstrap_permissions()
run_corp_update()
quit()
