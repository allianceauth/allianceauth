from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User

from eveonline.models import EveCharacter
from eveonline.models import EveCorporationInfo
from eveonline.models import EveApiKeyPair
from authentication.models import AuthServicesInfo


@python_2_unicode_compatible
class ApplicationQuestion(models.Model):
    title = models.CharField(max_length=254, verbose_name='Question')
    help_text = models.CharField(max_length=254, blank=True, null=True)
    multi_select = models.BooleanField(default=False)

    def __str__(self):
        return "Question: " + self.title


@python_2_unicode_compatible
class ApplicationChoice(models.Model):
    question = models.ForeignKey(ApplicationQuestion,on_delete=models.CASCADE,related_name="choices")
    choice_text = models.CharField(max_length=200, verbose_name='Choice')

    def __str__(self):
        return self.choice_text

@python_2_unicode_compatible
class ApplicationForm(models.Model):
    questions = models.ManyToManyField(ApplicationQuestion)
    corp = models.OneToOneField(EveCorporationInfo)

    def __str__(self):
        return str(self.corp)


@python_2_unicode_compatible
class Application(models.Model):
    form = models.ForeignKey(ApplicationForm, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    approved = models.NullBooleanField(blank=True, null=True, default=None)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    reviewer_character = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + " Application To " + str(self.form)

    class Meta:
        permissions = (
            ('approve_application', 'Can approve applications'), ('reject_application', 'Can reject applications'),
            ('view_apis', 'Can view applicant APIs'),)
        unique_together = ('form', 'user')

    @property
    def main_character(self):
        try:
            auth = AuthServicesInfo.objects.get(user=self.user)
            char = EveCharacter.objects.get(character_id=auth.main_char_id)
            return char
        except:
            return None

    @property
    def characters(self):
        return EveCharacter.objects.filter(user=self.user)

    @property
    def apis(self):
        return EveApiKeyPair.objects.filter(user=self.user)

    @property
    def reviewer_str(self):
        if self.reviewer_character:
            return str(self.reviewer_character)
        elif self.reviewer:
            return "User " + str(self.reviewer)
        else:
            return None


@python_2_unicode_compatible
class ApplicationResponse(models.Model):
    question = models.ForeignKey(ApplicationQuestion, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()

    def __str__(self):
        return str(self.application) + " Answer To " + str(self.question)

    class Meta:
        unique_together = ('question', 'application')


@python_2_unicode_compatible
class ApplicationComment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + " comment on " + str(self.application)


################
# Legacy Models
################
@python_2_unicode_compatible
class HRApplication(models.Model):
    character_name = models.CharField(max_length=254, default="")
    full_api_id = models.CharField(max_length=254, default="")
    full_api_key = models.CharField(max_length=254, default="")
    is_a_spi = models.CharField(max_length=254, default="")
    about = models.TextField(default="")
    extra = models.TextField(default="")

    corp = models.ForeignKey(EveCorporationInfo)
    user = models.ForeignKey(User)

    approved_denied = models.NullBooleanField(blank=True, null=True)
    reviewer_user = models.ForeignKey(User, blank=True, null=True, related_name="review_user")
    reviewer_character = models.ForeignKey(EveCharacter, blank=True, null=True)
    reviewer_inprogress_character = models.ForeignKey(EveCharacter, blank=True, null=True,
                                                      related_name="inprogress_character")

    def __str__(self):
        return self.character_name + " - Application"


@python_2_unicode_compatible
class HRApplicationComment(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    comment = models.CharField(max_length=254, default="")
    application = models.ForeignKey(HRApplication)
    commenter_user = models.ForeignKey(User)
    commenter_character = models.ForeignKey(EveCharacter)

    def __str__(self):
        return str(self.application.character_name) + " - Comment"
