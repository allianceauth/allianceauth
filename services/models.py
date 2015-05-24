from django.db import models

class TSgroup(models.Model):
	group_id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=30)
	
class AuthTS(models.Model):
	ts_group_id = models.ForeignKey(TSgroup)
	auth_group_id = models.ForeignKey('auth.Group')

class UserTSgroup(models.Model):
	user_id = models.ForeignKey('auth.User')
	group_id = models.ManyToManyField(TSgroup)