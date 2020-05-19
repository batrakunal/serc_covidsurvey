from django.conf.urls import url
from . import views

app_name = 'survey'

urlpatterns = [
    url(r'^submit/$', views.submit_survey, name="submit"),
    url(r'^confirmation/$', views.view_survey_confirmation, name="confirmation"),
    url(r'^save/$', views.save_survey, name="save"),
    url(r'^output-submission-pdf/$', views.output_submission_pdf, name="output_pdf"),
    url(r'^(?P<slug>[\w-]+)/$', views.view_survey, name="survey"),
]