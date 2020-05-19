from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_survey_complete = models.BooleanField(default=False)
    last_survey_save = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.username
