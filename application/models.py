from __future__ import unicode_literals
from django.db import models
from django.forms.models import model_to_dict

# Create your models here.
class User(models.Model):
    class Meta():
        index_together = [['id']]
    userName = models.CharField(max_length=100, null=True)
    userEmail = models.CharField(max_length=300, null=True)
    userCreditCardNumber = models.CharField(max_length=20, null=True)
    userLanguage = models.CharField(max_length=20, null=True)
    validFlag = models.SmallIntegerField(null=True)

    def __str__(self):
        return self.id

class Works(models.Model):
    class Meta():
        index_together = [['user']]
    user = models.ForeignKey(User, models.CASCADE, default=1)
    workTitle = models.CharField(max_length=100, null=True)
    WordsOriginal = models.CharField(max_length=300, null=True)
    lc_src = models.CharField(max_length=3, null=True)
    lc_tgt = models.CharField(max_length=3, null=True)
    progress = models.IntegerField(null=True)
    createdDate = models.DateField(null=True)
    numberofchar = models.IntegerField(null=True)
    status = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.id
