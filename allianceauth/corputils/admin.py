from django.contrib import admin

from .models import CorpStats, CorpMember

admin.site.register(CorpStats)
admin.site.register(CorpMember)