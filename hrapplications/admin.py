from __future__ import unicode_literals
from django.contrib import admin

from hrapplications.models import Application
from hrapplications.models import ApplicationQuestion
from hrapplications.models import ApplicationForm
from hrapplications.models import ApplicationResponse
from hrapplications.models import ApplicationComment
from hrapplications.models import ApplicationChoice

class ChoiceInline(admin.TabularInline):
    model = ApplicationChoice
    extra = 0
    verbose_name_plural = 'Choices (optional)'
    verbose_name= 'Choice'

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,      {'fields': ['title', 'help_text', 'multi_select']}),
            ]
    inlines = [ChoiceInline]

admin.site.register(Application)
admin.site.register(ApplicationComment)
admin.site.register(ApplicationQuestion, QuestionAdmin)
admin.site.register(ApplicationForm)
admin.site.register(ApplicationResponse)
