from django.urls import path, re_path, include
from application import views_main, views_work, views_user, views_landing, views_settings
from django.contrib.auth.views import LoginView
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
    # path('login/', views_user.customlogin, name='login'),
    path('login/', LoginView.as_view(form_class=EmailAuthenticationForm, template_name='registration/login.html'), name='login'),
    path('userMaintenance/', views_user.maintenance, name='userMaintenance'),
    path('forgotPassword/', views_user.forgotPassword, name='forgotPassword'),

    # The work page functions
    path('addwork/', views_work.addwork, name='addwork'),
    path('addwork/saveWork', views_work.saveWork, name='saveWork'),
    path('workdetail/<int:work_id>/', views_work.workdetail, name='workdetail'),
    path('addTag', views_work.addTag, name='addTag'),
    path('removeTag', views_work.removeTag, name='removeTag'),
    path('getTargetLang', views_work.getTargetLang, name='getTargetLang'),
    path('requestGengoTranslation', views_work.requestGengoTranslation, name='requestGengoTranslation'),
    path('requestGoogleTranslation', views_work.requestGoogleTranslation, name='requestGoogleTranslation'),
    path('workdetail/<int:work_id>/gethistory', views_work.gethistory, name='gethistory'),
    path('saveGengoTranslation', views_work.saveGengoTranslation, name='saveGengoTranslation'),
    path('saveGoogleTranslation', views_work.saveGoogleTranslation, name='saveGoogleTranslation'),
    path('saveSelfTranslation', views_work.saveSelfTranslation, name='saveSelfTranslation'),
    path('deleteHistory', views_work.deleteHistory, name='deleteHistory'),
    path('worklist/', views_work.worklist, name='worklist'),

    # The setting page functions
    path('glossarylist/', views_settings.glossarylist, name='glossarylist'),
    path('glossarylist/createGlossary', views_settings.createGlossary, name='createGlossary'),
    path('glossarydetail/<int:glossary_id>/', views_settings.glossarydetail, name='glossarydetail'),
    path('updateGlossary/', views_settings.updateGlossary, name='updateGlossary'),

    path('taglist/', views_settings.taglist, name='taglist'),

    path('i18n/', include('django.conf.urls.i18n'))
]
