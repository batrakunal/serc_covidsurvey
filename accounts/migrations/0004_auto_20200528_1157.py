# Generated by Django 2.2.5 on 2020-05-28 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_surveyuser_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveyuser',
            name='token',
            field=models.CharField(default='9949', max_length=4),
        ),
    ]
