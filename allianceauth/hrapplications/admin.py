from django.contrib import admin

from .models import Application, ApplicationChoice, ApplicationComment, ApplicationForm, ApplicationQuestion, \
    ApplicationResponse


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
