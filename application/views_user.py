from django.contrib.auth import login, authenticate
from application.forms import SignupForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from application.models import CustomUser, Language, DisplayLanguage
from application.customlib import DataLib, CookieLib

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'user_signup.html', {'form': form})

def forgotPassword(request):
    return render(request, 'app/user_forgotpassword.html')

@login_required
def personalsetting(request):
    CookieLib.setLanguage(request)
    user = CustomUser.objects.filter(id=request.user.id).first()
    displayLangs = DisplayLanguage.objects.all()
    selecteddisplayLang = DisplayLanguage.objects.filter(language=user.userLanguage).first()
    langs = Language.objects.filter(validFlag=1).extra(select = { 'displaylang' : request.user.userLanguage}).values('lc','language', 'displaylang').order_by('displaylang')
    dlib = DataLib()
    selectedlang = dlib.getUserLang(request)
    data = {
        'user' : user,
        'displayLangs' :displayLangs,
        'selecteddisplayLang' :selecteddisplayLang,
        'langs' :langs,
        'selectedlang' : selectedlang,
    }
    return render(request, 'app/user_personalsetting.html', data)

@login_required
def groupsetting(request):
    CookieLib.setLanguage(request)
    return render(request, 'app/user_groupsetting.html')
