from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


def get_token():
    return get_random_string(length=4, allowed_chars='123456789')


class CustomUser(AbstractUser):
    is_survey_complete = models.BooleanField(default=False)
    last_survey_save = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.username


class SurveyUser(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    is_survey_complete = models.BooleanField(default=False)
    last_survey_save = models.DateTimeField(default=None, null=True)
    token = models.CharField(max_length=4, default=get_token)

    def __str__(self):
        return self.email
