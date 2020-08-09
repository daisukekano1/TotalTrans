from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.forms.models import model_to_dict

# Create your models here.
class User(models.Model):
    class Meta():
        index_together = [['id']]
    userName = models.CharField(max_length=100, null=True)
    userEmail = models.CharField(max_length=300, null=True)
    userCreditCardNumber = models.CharField(max_length=20, null=True)
    userLanguage = models.CharField(max_length=20, null=True)
    defaultLcSrc = models.CharField(max_length=5, null=True)
    defaultLcTgt = models.CharField(max_length=5, null=True)
    validFlag = models.SmallIntegerField(null=True)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id

class Works(models.Model):
    class Meta():
        index_together = [['user']]
    user = models.ForeignKey(User, models.CASCADE, default=1)
    workTitle = models.CharField(max_length=100, null=True)
    wordsOriginal = models.TextField(null=True)
    lc_src = models.CharField(max_length=5, null=True)
    lc_tgt = models.CharField(max_length=5, null=True)
    progress = models.IntegerField(null=True)
    createdDate = models.DateTimeField(default=timezone.now)
    numberofchar = models.IntegerField(null=True)
    wordsTranslated = models.TextField(null=True)
    status = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.id

class Language(models.Model):
    class Meta():
        index_together = [['lc']]
    lc = models.CharField(max_length=5, null=True)
    language = models.CharField(max_length=50, null=True)
    flagId = models.CharField(max_length=5, null=True)
    japanese = models.CharField(max_length=30, null=True)
    english = models.CharField(max_length=30, null=True)
    spanish = models.CharField(max_length=30, null=True)
    chineseTra = models.CharField(max_length=30, null=True)
    chineseSim = models.CharField(max_length=30, null=True)
    korean = models.CharField(max_length=30, null=True)
    validFlag = models.SmallIntegerField(null=True)

    def __str__(self):
        return self.id

class TranslationHistory(models.Model):
    class Meta():
        index_together = [['id']]
    work = models.ForeignKey(Works, models.CASCADE, default=1)
    historyNum = models.IntegerField(null=True)
    beforeTranslation = models.TextField(null=True)
    afterTranslation = models.TextField(null=True)
    TranslationType = models.CharField(max_length=10, null=True)
    jobid = models.CharField(max_length=20, null=True)
    deleteFlag = models.SmallIntegerField(null=True)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id

    class Meta:
        get_latest_by = ['id']

class UserTag(models.Model):
    class Meta():
        index_together = [['user_id']]
    user = models.ForeignKey(User, models.CASCADE, default=1)
    tagname = models.CharField(max_length=100, null=True)
    backgroundcolor = models.CharField(max_length=8, null=True)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id

class WorkUserTag(models.Model):
    class Meta():
        index_together = [['work_id']]
    work = models.ForeignKey(Works, models.CASCADE, default=1)
    tag = models.ForeignKey(UserTag, models.CASCADE, default=1)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
