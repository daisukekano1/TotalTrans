from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.dispatch import Signal
from allauth.account.signals import user_logged_in # it signal for post login
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.utils import translation

@receiver(user_logged_in) # Decorator of receiving signal while user going to logged in
def post_login(sender, user, request, response, **kwargs):
    user_language = 'ja'
    translation.activate(user_language)
    response = HttpResponse(...)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
    return response