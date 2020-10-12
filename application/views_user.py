from django.contrib.auth import login, authenticate
from application.forms import SignupForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
    return render(request, 'app/user_personalsetting.html')

@login_required
def groupsetting(request):
    return render(request, 'app/user_groupsetting.html')
