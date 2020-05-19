import io
import re
from time import gmtime, strftime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

from accounts.models import CustomUser
from .models import Answer, get_answers_by_user, get_all_question_in_survey, get_survey_by_slug


@login_required
def view_survey(request, slug):
    if request.user.is_survey_complete:
        return redirect('profile')
    # get current survey by slug
    survey_list = get_survey_by_slug(slug)
    if len(survey_list) == 0:
        return redirect('home')
    survey_obj = survey_list[0]
    # construct data for view
    data = {'sections': get_section_dict(survey_obj),
            'answers': get_answer_dict_in_user(request.user.id)}

    return render(request, 'survey.html', data)


@login_required
def view_survey_confirmation(request):
    if not request.user.is_survey_complete:
        return redirect('profile')
    answers = get_answers_by_user(request.user.id)
    questions = get_all_question_in_survey("covid")
    answers_dict = get_questionId_answer_dict(answers)
    # add data into pdf content
    data = {}
    for question in questions:
        if question.section.name not in data:
            data[question.section.name] = {}
        data[question.section.name][question.content] = answers_dict.get(question.id, "Didn't answer")

    return render(request, 'confirmation.html', {'data': data})


@login_required
def output_submission_pdf(request):
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
                Paragraph('Account: ' + request.user.username, styles['Info'])]
    # prepare data
    answers = get_answers_by_user(request.user.id)
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
@login_required
def save_survey(request):
    if request.method == "POST":
        answer_list = []
        for key in request.POST:
            if key == 'csrfmiddlewaretoken':
                continue
            answer_list.append(Answer(question_id=key, content=request.POST[key], user_id=request.user.id))

        Answer.objects.filter(user_id=request.user.id).delete()
        Answer.objects.bulk_create(answer_list)
        CustomUser.objects.filter(id=request.user.id).update(last_survey_save=timezone.now())

        return JsonResponse({})
    else:
        return HttpResponse('Invalid HTTP method', status=400)


# submit
@login_required
def submit_survey(request):
    if request.method == "POST":
        CustomUser.objects.filter(id=request.user.id).update(is_survey_complete=True, last_survey_save=timezone.now())

        return redirect('/survey/confirmation')
    else:
        return redirect('home')


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
