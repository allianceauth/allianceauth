from django.contrib import admin

from models import Application
from models import ApplicationQuestion
from models import ApplicationForm
from models import ApplicationResponse
from models import ApplicationComment

admin.site.register(Application)
admin.site.register(ApplicationComment)
admin.site.register(ApplicationQuestion)
admin.site.register(ApplicationForm)
admin.site.register(ApplicationResponse)
