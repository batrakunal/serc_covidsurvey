import io
import re
from time import gmtime, strftime

from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

from accounts.models import SurveyUser
from .models import Answer, get_answers_by_user, get_all_question_in_survey, get_survey_by_slug


def isValidEmail(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False


def retrieve(request):
    email = request.GET.get('email', '')
    return render(request, 'retrieve.html', {'email': email})


def view_survey(request, slug):
    if request.method != "POST":
        return redirect('home')

    if not isValidEmail(request.POST.get('email', '')):
        return HttpResponse('Invalid Email address', status=400)

    email = request.POST['email']
    try:
        user = SurveyUser.objects.get(email=email)
    except SurveyUser.DoesNotExist:
        user = SurveyUser.objects.create(email=email)

    if user.is_survey_complete:
        return redirect('/survey/retrieve?email='+email)

    # get current survey by slug
    survey_list = get_survey_by_slug(slug)
    if len(survey_list) == 0:
        return redirect('home')
    survey_obj = survey_list[0]
    # construct data for view
    data = {'sections': get_section_dict(survey_obj),
            'answers': get_answer_dict_in_user(user.id),
            'uid': user.id,
            'token': user.token}

    return render(request, 'survey.html', data)


def view_survey_confirmation(request):
    if request.method != "POST":
        return redirect('home')

    email = request.POST.get('email', None)
    uid = request.POST.get('uid', None)
    token = request.POST.get('token', None)

    if email is not None:
        try:
            user = SurveyUser.objects.get(email=email, token=token)
        except SurveyUser.DoesNotExist:
            return render(request, 'retrieve.html', {'email': email, 'error': 'Authentication failed'})
    else:
        try:
            user = SurveyUser.objects.get(id=uid, token=token)
        except SurveyUser.DoesNotExist:
            return HttpResponse('Invalid Auth', status=400)

    # for submit
    if not user.is_survey_complete:
        user.is_survey_complete = True
        user.last_survey_save = timezone.now()
        user.save()

    answers = get_answers_by_user(user.id)
    questions = get_all_question_in_survey("covid")
    answers_dict = get_questionId_answer_dict(answers)
    # add data into pdf content
    data = {}
    for question in questions:
        if question.section.name not in data:
            data[question.section.name] = {}
        data[question.section.name][question.content] = answers_dict.get(question.id, "Didn't answer")

    return render(request, 'confirmation.html', {'data': data, 'user': user})


def output_submission_pdf(request):
    uid = request.GET.get('uid', None)
    token = request.GET.get('token', None)

    try:
        user = SurveyUser.objects.get(id=uid, token=token)
    except SurveyUser.DoesNotExist:
        return HttpResponse('Invalid Auth', status=400)

    buffer = io.BytesIO()
    # pdf init
    doc = SimpleDocTemplate(buffer, bottomMargin=45, topMargin=55, rightMargin=50, leftMargin=50,
                            title="Model-Based Systems Engineering Maturity Benchmark Survey",
                            author="Systems Engineering Research Center", )
    # pdf styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ColorTitle', parent=styles['Title'], textColor=colors.HexColor("#8c2131")));
    styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], textColor=colors.HexColor("#4966b1")));
    styles.add(ParagraphStyle(name='Info', parent=styles['Normal'], fontSize=13, spaceAfter=10, spaceBefore=10));
    styles.add(ParagraphStyle(name='Question', parent=styles['Normal'], fontSize=13, spaceAfter=10, spaceBefore=10,
                              leading=18));
    styles.add(ParagraphStyle(name='Answer', parent=styles['Normal'], fontSize=13, spaceAfter=15,
                              textColor=colors.HexColor("#8c2131"), leading=18));
    # pdf content
    elements = [Paragraph('SERC COVID-19 Impact Survey', styles['ColorTitle']),
                Paragraph('Output Time: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()), styles['Info']),
                Paragraph('Email: ' + user.email, styles['Info']),
                Paragraph('Submission ID: ' + user.token, styles['Info'])]
    # prepare data
    answers = get_answers_by_user(user.id)
    questions = get_all_question_in_survey("covid")
    answers_dict = get_questionId_answer_dict(answers)
    # add data into pdf content
    last_section_name = ""
    for question in questions:
        if question.section.name != last_section_name:
            elements.append(Paragraph(question.section.name, styles['Section']))
        last_section_name = question.section.name
        elements.append(Paragraph(question.content, styles['Question']))
        answer_str_list = answers_dict.get(question.id, "Didn't answer").split(';;;')
        for idx in range(len(answer_str_list)):
            answer_str_list[idx] = add_space_between_choice_answer(answer_str_list[idx])

        answer_str = '<br/><br/>'.join(answer_str_list)
        elements.append(Paragraph(answer_str, styles['Answer']))
    # build pdf
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='output-' + strftime("%Y-%m-%d %H:%M", gmtime()) + '.pdf')


# save
def save_survey(request):
    if request.method != "POST":
        return HttpResponse('Invalid HTTP method', status=400)

    uid = request.POST.get('uid', None)
    token = request.POST.get('token', None)

    try:
        user = SurveyUser.objects.get(id=uid, token=token)
    except SurveyUser.DoesNotExist:
        return HttpResponse('Invalid Auth', status=400)

    if user.is_survey_complete:
        return HttpResponse('Invalid Request', status=400)

    answer_list = []
    for key in request.POST:
        if key == 'csrfmiddlewaretoken' or key == 'token' or key == 'uid':
            continue
        answer_list.append(Answer(question_id=key, content=request.POST[key], user_id=user.id))

    Answer.objects.filter(user_id=user.id).delete()
    Answer.objects.bulk_create(answer_list)
    SurveyUser.objects.filter(id=user.id).update(last_survey_save=timezone.now())

    return JsonResponse({})


# Helper: for survey
def get_section_dict(survey_obj):
    sections = survey_obj.get_section_in_survey()
    section_dict = {}
    for section in sections:
        questions = section.get_question_in_section()
        question_list = get_question_list(questions)
        section_dict[section.name] = question_list
    return section_dict


# Helper: for survey section
def get_question_list(questions):
    question_list = []
    for question in questions:
        choice_list = str(question.get_choice_in_question()).split(';')
        question_dict = {
            'id': question.id,
            'name': question.content,
            'type': question.type,
            'choice': choice_list
        }
        question_list.append(question_dict)
    return question_list


# Helper: for survey
def get_answer_dict_in_user(user_id):
    answers = get_answers_by_user(user_id)
    answer_dict = {}
    for answer in answers:
        answer_dict[answer.question_id] = answer.content
    return answer_dict


# Helper: for output submission in pdf
def get_questionId_answer_dict(answers):
    val = {}
    for answer in answers:
        if not answer.content: continue
        val[answer.question_id] = answer.content
    return val


# Helper: change '[choice]answer' to '[choice] answer' || '[[choice]]answer' to '[[choice]] answer'
def add_space_between_choice_answer(answer):
    search_result = re.search(r'\]([^\]]|$)', answer)
    if search_result:
        return answer[:search_result.start() + 1] + " " + answer[search_result.start() + 1:]
    return answer
