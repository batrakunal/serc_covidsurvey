from django.conf.urls import url
from . import views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.construct_export, name="dashboard_home"),
    url(r'^summary/$', views.construct_dashboard_summary, name="summary"),
    # url(r'^summary/spider/$', views.construct_spider_chart, name="spider"),
    # url(r'^summary/stacked/$', views.construct_stacked_chart, name="stacked"),
    url(r'^submission/(?P<id>[\w@.\-_+]+)/$', views.construct_dashboard_submission_single, name="submission_single"),
    url(r'^submission/$', views.construct_dashboard_submission, name="submission"),
    url(r'^export/$', views.construct_export, name='export'),
    url(r'^export/export-excel/$', views.export_to_xls, name='export_xls'),
    url(r'^export/export-text/$', views.export_text, name='export_text'),
]
