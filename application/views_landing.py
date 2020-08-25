from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse
from application.models import Works, Language, WorkUserTag

def index(request):
    return render(request, 'app/landing_index.html')
