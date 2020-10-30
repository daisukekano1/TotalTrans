from django.urls import path, re_path, include
from application import views_main, views_work, views_user, views_landing, views_settings, views_history, views_lisence
from django.contrib.auth.views import LoginView, LogoutView
from application.forms import EmailAuthenticationForm

urlpatterns = [
    # The landing page functions
    path('', views_landing.index, name='index'),

    # The main page functions
    path('home', views_main.home, name='home'),
    path('contact/', views_main.contact, name='contact'),
    path('submitContact/', views_main.submitContact, name='submitContact'),
    path('termsanduse/', views_main.termsanduse, name='termsanduse'),
    path('manual/', views_main.manual, name='manual'),

    # The account page functions
    path('signup/', views_user.signup, name='signup'),
    path('login/', LoginView.as_view(form_class=EmailAuthenticationForm, template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/login.html'), name='logout'),

    path('personalsetting/', views_user.personalsetting, name='personalsetting'),
    path('saveAccountsetting', views_user.saveAccountsetting, name='saveAccountsetting'),
    path('saveLanguagesetting', views_user.saveLanguagesetting, name='saveLanguagesetting'),
    path('groupsetting/', views_user.groupsetting, name='groupsetting'),
    path('forgotPassword/', views_user.forgotPassword, name='forgotPassword'),

    # The work page functions
    path('workcreation/', views_work.workcreation, name='workcreation'),
    path('workcreation/<int:work_id>/', views_work.workcreation, name='workcreation'),
    path('savework', views_work.savework, name='saveWork'),
    path('startTranslation', views_work.startTranslation, name='startTranslation'),
    path('workdetail/<int:work_id>/', views_work.workdetail, name='workdetail'),
    path('addTag', views_work.addTag, name='addTag'),
    path('removeTag', views_work.removeTag, name='removeTag'),
    path('requestGengoTranslation', views_work.requestGengoTranslation, name='requestGengoTranslation'),
    path('requestGoogleTranslation', views_work.requestGoogleTranslation, name='requestGoogleTranslation'),
    path('workdetail/<int:work_id>/gethistory', views_work.gethistory, name='gethistory'),
    path('saveGoogleTranslation', views_work.saveGoogleTranslation, name='saveGoogleTranslation'),
    path('saveSelfTranslation', views_work.saveSelfTranslation, name='saveSelfTranslation'),
    path('saveIgnoreTranslation', views_work.saveIgnoreTranslation, name='saveIgnoreTranslation'),
    path('deleteHistory', views_work.deleteHistory, name='deleteHistory'),
    path('worklist/', views_work.worklist, name='worklist'),
    path('workstart/<int:work_id>/', views_work.workstart, name='workstart'),
    path('workclose/<int:work_id>/', views_work.workclose, name='workclose'),
    path('workreopen/<int:work_id>/', views_work.workreopen, name='workreopen'),
    path('getTextfromURL', views_work.getTextfromURL, name='getTextfromURL'),

    path('translationHistory/', views_work.history, name='translationHistory'),
    path('translationHistory/gethistory', views_work.gethistory, name='gethistory'),

    # The setting page functions
    path('glossary/', views_settings.glossary, name='glossary'),
    path('glossary/createGlossary', views_settings.createGlossary, name='createGlossary'),
    path('glossary/save', views_settings.saveGlossary, name='saveGlossary'),
    path('getglossarylist/', views_settings.getglossarylist, name='getglossarylist'),

    path('taglist/', views_settings.taglist, name='taglist'),
    path('taglist/gettags', views_settings.gettags, name='gettags'),
    path('taglist/<int:tag_id>/deleteTag', views_settings.deleteTag, name='deleteTag'),
    path('getworksfortag', views_settings.getworksfortag, name='getworksfortag'),
    path('taglist/savetaglist', views_settings.savetaglist, name='savetaglist'),

    path('activatelisence/', views_lisence.activatelisence, name='activatelisence'),
    path('lisenceactivationsave', views_lisence.saveactivatelisence, name='saveactivatelisence'),


    path('i18n/', include('django.conf.urls.i18n'))

]
