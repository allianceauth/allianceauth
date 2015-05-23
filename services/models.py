from django.db import models

class authTS(models.Model):
	ts_group_id = models.ForeignKey(TSgroup)
	auth_group_id = models.ForeignKey(Group)

class TSgroup(models.Model):
	group_id = models.int(primary_key=True)
	name = models.CharField(max_length=30)

class userTSgroup(model.Model):
	user_id = models.ForeignKey(User)
    group_id = model.ManyToManyField(TSgroup)