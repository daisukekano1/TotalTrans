from django.urls import path, re_path, include
from application import views

urlpatterns = [
    # The home page
    path('', views.index, name='index'),
    path('addwork/', views.addwork, name='addwork'),
    path('addwork/saveWork', views.saveWork, name='saveWork'),
    path('workdetail/<int:work_id>/', views.workdetail, name='workdetail'),
    path('addTag', views.addTag, name='addTag'),
    path('removeTag', views.removeTag, name='removeTag'),
    path('getTargetLang', views.getTargetLang, name='getTargetLang'),
    path('requestGengoTranslation', views.requestGengoTranslation, name='requestGengoTranslation'),
    path('requestGoogleTranslation', views.requestGoogleTranslation, name='requestGoogleTranslation'),
    path('workdetail/<int:work_id>/gethistory', views.gethistory, name='gethistory'),
    path('saveGengoTranslation', views.saveGengoTranslation, name='saveGengoTranslation'),
    path('saveGoogleTranslation', views.saveGoogleTranslation, name='saveGoogleTranslation'),
    path('saveSelfTranslation', views.saveSelfTranslation, name='saveSelfTranslation'),
    path('deleteHistory', views.deleteHistory, name='deleteHistory'),
    path('i18n/', include('django.conf.urls.i18n')),
]
