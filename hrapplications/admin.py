from __future__ import unicode_literals
from django.contrib import admin

from hrapplications.models import Application
from hrapplications.models import ApplicationQuestion
from hrapplications.models import ApplicationForm
from hrapplications.models import ApplicationResponse
from hrapplications.models import ApplicationComment

admin.site.register(Application)
admin.site.register(ApplicationComment)
admin.site.register(ApplicationQuestion)
admin.site.register(ApplicationForm)
admin.site.register(ApplicationResponse)
