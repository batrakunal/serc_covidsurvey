from django.contrib import admin
from .models import Survey, Answer
from .models import Question
from .models import Section
from .models import Choice

# Register your models here.
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Section)
admin.site.register(Choice)
admin.site.register(Answer)

