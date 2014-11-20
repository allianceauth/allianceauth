from django.contrib import admin

from models import HRApplication
from models import HRApplicationComment

admin.site.register(HRApplication)
admin.site.register(HRApplicationComment)