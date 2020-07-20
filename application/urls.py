from django.urls import path, re_path, include
from application import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.list_html, name='application'),

    # The home page
    path('', views.index, name='index'),
    path('workdetail/<int:work_id>/', views.workdetail, name='workdetail'),
    path('addwork/', views.addwork, name='addwork'),
    path('i18n/', include('django.conf.urls.i18n')),
]
