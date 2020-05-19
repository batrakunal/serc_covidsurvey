from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, include

from . import views

urlpatterns = [
    path(r'', views.homepage, name='home'),
    path(r'survey/', include('survey.urls')),
    path(r'dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()