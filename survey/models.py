from django.db import models
from accounts.models import SurveyUser


class Survey(models.Model):
    name = models.CharField(max_length=400)
    description = models.TextField()
    slug = models.SlugField(null=True)

    def __str__(self):
        return self.name

    def get_section_in_survey(self):
        return self.section.all()


class Section(models.Model):
    survey = models.ForeignKey(Survey, null=True, on_delete=models.CASCADE, related_name='section')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def get_question_in_section(self):
        return self.question.all()

    class Meta:
        ordering = ['order']


class Question(models.Model):
    TEXT = 'text'
    CHOICE = 'choice'
    CHOICE_TEXT = 'choice-text'

    QUESTION_TYPES = (
        (TEXT, 'text'),
        (CHOICE, 'choice'),
        (CHOICE_TEXT, 'choice-text'),
    )

    section = models.ForeignKey(Section, null=True, on_delete=models.CASCADE, related_name='question')
    content = models.CharField(max_length=1000)
    type = models.CharField(max_length=200, choices=QUESTION_TYPES, default=CHOICE)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.content

    def get_choice_in_question(self):
        return self.choice.first()

    class Meta:
        ordering = ['order']


class Choice(models.Model):
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE, related_name='choice')
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.content


class Answer(models.Model):
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(SurveyUser, null=True, on_delete=models.SET_NULL)
    content = models.TextField()

    class Meta:
        unique_together = ['question', 'user']
        ordering = ['question_id']

    def __str__(self):
        return self.content


class QuestionResource(models.Model):
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE, related_name='question_resource')
    content = models.CharField(max_length=100)

    def __str__(self):
        return self.content


def get_answers_by_user(user_id):
    return Answer.objects.filter(user_id=user_id)


def get_survey_by_slug(slug):
    return Survey.objects.filter(slug=slug)


def get_all_question_in_survey(survey_slug):
    survey_list = Survey.objects.filter(slug=survey_slug)
    survey_obj = survey_list[0]
    sections = survey_obj.get_section_in_survey()
    question_list = []
    for section in sections:
        questions = section.get_question_in_section()
        for question in questions:
            question_list.append(question)
    return question_list
