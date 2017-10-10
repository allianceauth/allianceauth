import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allianceauth.project_template.project_name.settings.base')

from django.conf import settings  # noqa

app = Celery('alliance_auth')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
