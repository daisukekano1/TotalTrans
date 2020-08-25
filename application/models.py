from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('Email address'), unique=True)
    username2 = models.CharField(_('User name'), max_length=30, blank=False, default='')
    userCreditCardNumber = models.CharField(max_length=20, null=True)
    userLanguage = models.CharField(max_length=20, null=True)
    defaultLcSrc = models.CharField(max_length=5, null=True)
    defaultLcTgt = models.CharField(max_length=5, null=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Works(models.Model):
    class Meta():
        index_together = [['user']]
    user = models.ForeignKey(CustomUser, models.CASCADE, default=1)
    workTitle = models.CharField(max_length=100, null=True)
    wordsOriginal = models.TextField(null=True)
    lc_src = models.CharField(max_length=5, null=True)
    lc_tgt = models.CharField(max_length=5, null=True)
    progress = models.IntegerField(null=True)
    createdDate = models.DateTimeField(default=timezone.now)
    numberofchar = models.IntegerField(null=True)
    wordsTranslated = models.TextField(null=True)
    status = models.CharField(max_length=10, null=True)
    eta = models.DateTimeField(null=True)

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
    user = models.ForeignKey(CustomUser, models.CASCADE, default=1)
    tagname = models.CharField(max_length=100, null=True)
    backgroundcolor = models.CharField(max_length=8, null=True)
    validFlg = models.SmallIntegerField(null=False, default=1)
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

class UserGlossary(models.Model):
    class Meta():
        index_together = [['user_id']]
    user = models.ForeignKey(CustomUser, models.CASCADE, default=1)
    filename = models.CharField(max_length=100, null=True)
    fileid = models.CharField(max_length=100, null=True)
    numberofcount = models.IntegerField(null=True)
    lc_src = models.CharField(max_length=5, null=True)
    lc_tgt = models.CharField(max_length=5, null=True)
    validFlg = models.SmallIntegerField(null=False, default=1)
    createdDate = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id

