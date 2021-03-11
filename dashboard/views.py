import io
from time import gmtime, strftime

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import FileResponse
from django.shortcuts import render, redirect

from survey.models import Survey, Answer, get_all_question_in_survey

from django.http import HttpResponse
from accounts.models import SurveyUser


@login_required
def construct_dashboard_home(request):
    if not request.user.is_staff:
        return redirect('profile')
    return render(request, 'dashboard_home.html', {})


@login_required
def construct_dashboard_summary(request):
    if not request.user.is_staff:
        return redirect('profile')
    # URL parameters
    sample = request.GET.get('sample')

    # get answers
    all_answers = get_all_answers()
    all_answers_users = get_all_answers_users()
    completed_answers_users = SurveyUser.objects.filter(is_survey_complete=1)
    effective_answers_users = get_effective_answers_users(all_answers_users)

    # sample filter
    filtered_result = sample_filter(sample, all_answers, all_answers_users, effective_answers_users, completed_answers_users)
    computed_answers = filtered_result.get("computed_answers")
    computed_answers_users = filtered_result.get("computed_answers_users")

    # go through answers
    question_list = []
    sections = get_all_sections()
    for section in sections:
        for quest in section.get_question_in_section():
            question_dict = {"id": quest.id,
                             "content": quest.content,
                             "type": quest.type,
                             "section": section.name}
            answer_list = get_all_answer_by_question_id(computed_answers, quest.id)
            question_dict["answers"] = answer_list
            question_dict["count"] = len(answer_list)
            if quest.type == "choice" or quest.type == "degree" :
                choice = quest.get_choice_in_question()
                question_dict["choice"] = choice.content
                question_dict["choice_counted"] = count_choice_answer(choice.content, answer_list)
            elif quest.type == "choice-text":
                choice = quest.get_choice_in_question()
                question_dict["choice"] = choice.content
                question_dict["choice_counted"] = count_choice_answer(choice.content, answer_list)
            elif quest.type == "choice-multi-text":
                choice = quest.get_choice_in_question()
                question_dict["choice"] = choice.content
                question_dict["choice_counted"] = count_multi_choice_answer(choice.content, answer_list)
            question_list.append(question_dict.copy())

    # data for template
    data = {"question_list": question_list,
            "number_of_completed_survey": completed_answers_users.count(),
            "number_of_participant": all_answers_users.count(),
            "number_of_effective_participant": effective_answers_users.count(),
            "number_of_computed_participant": computed_answers_users.count(),
            }
    return render(request, 'dashboard_summary.html', data)


@login_required
def construct_dashboard_submission(request):
    if not request.user.is_staff:
        return redirect('profile')
    all_user = SurveyUser.objects.all()
    data = {"all_user": all_user}

    return render(request, 'dashboard_submission.html', data)


@login_required
def construct_dashboard_submission_single(request, id):
    if not request.user.is_staff:
        return redirect('profile')
    users = SurveyUser.objects.filter(id=id)
    if len(users) == 0:
        return redirect('dashboard:submission')

    user_id = users[0].id
    answers = Answer.objects.filter(user_id=user_id).order_by('question_id')

    sections = {}
    dict = {}
    for answer in answers:
        question = answer.question
        if question.section not in sections:
            dict.clear()
        dict[str(question.id) + ' ' + question.content] = answer.content
        sections[question.section] = dict.copy()

    # construct data for view
    data = {'sections': sections,
            'survey_username': id}

    return render(request, 'dashboard_submission_single.html', data)


# @login_required
# def construct_spider_chart(request):
#     if not request.user.is_staff:
#         return redirect('profile')
#
#     # URL parameters
#     sample = request.GET.get('sample')
#
#     # get answers
#     all_answers = get_all_answers()
#     all_answers_users = get_all_answers_users()
#     completed_answers_users = CustomUser.objects.filter(is_survey_complete=1)
#     effective_answers_users = get_effective_answers_users(all_answers_users)
#     # sample filter
#     filtered_result = sample_filter(sample, all_answers, all_answers_users, effective_answers_users, completed_answers_users)
#     computed_answers = filtered_result.get("computed_answers")
#
#     # go through answers
#     label_list = []
#     data_list = []
#     sections = get_all_sections()
#     for section in sections:
#         average_agree_rate = 0
#         count = 0
#         for quest in section.get_question_in_section():
#             answer_list = get_all_answer_by_question_id(computed_answers, quest.id)
#             agree_rate = count_agree_rate(answer_list)
#             if agree_rate:
#                 average_agree_rate += agree_rate
#                 count += 1
#         average_agree_rate = average_agree_rate / count if count else None
#         if average_agree_rate:
#             label_list.append(section.name)
#             data_list.append(round(average_agree_rate, 3))
#
#     data = {"number_of_completed_survey": completed_answers_users.count(),
#             "number_of_participant": all_answers_users.count(),
#             "number_of_effective_participant": effective_answers_users.count(),
#             'label_list': label_list,
#             'data_list': data_list
#             }
#     return render(request, 'dashboard_summary_spider_chart.html', data)


def transpose(l):
    return list(map(list, zip(*l)))


# def get_stacked_counted_list(choice, choice_group, question_id, answers):
#     choice_group_list = choice_group.split(",")
#     counted_list = []
#     for group in choice_group_list:
#         group_users = answers.filter(content=group).values('user_id')
#         group_answers = list(
#             answers.filter(user_id__in=group_users.values('user_id'), question_id=question_id).values_list('content',
#                                                                                                            flat=True))
#         counted_list.append(count_choice_answer(choice, group_answers))
#     return transpose(counted_list)


# @login_required
# def construct_stacked_chart(request):
#     if not request.user.is_staff:
#         return redirect('profile')
#
#     # URL parameters
#     sample = request.GET.get('sample')
#     question_id = request.GET.get('question-id')
#
#     # get answers
#     all_answers = get_all_answers()
#     all_answers_users = get_all_answers_users()
#     completed_answers_users = CustomUser.objects.filter(is_survey_complete=1)
#     effective_answers_users = get_effective_answers_users(all_answers_users)
#     # sample filter
#     filtered_result = sample_filter(sample, all_answers, all_answers_users, effective_answers_users, completed_answers_users)
#     computed_answers = filtered_result.get("computed_answers")
#
#     # go through answers
#     question_list = []
#     sections = get_all_sections()
#     for section in sections:
#         for quest in section.get_question_in_section():
#             if quest.type != "choice": continue
#             choice = quest.get_choice_in_question()
#             if choice.content != "Strongly Agree,Agree,Disagree,Strongly Disagree": continue
#             question_dict = {"id": quest.id, "content": quest.content, "type": quest.type, "section": section.name,
#                              "choice": choice.content}
#             if str(question_id) == str(quest.id):
#                 org_type_stacked_label = "government,industry,academia"
#                 org_size_stacked_label = "<500,501-2000,2001-10000,>10000"
#                 applied_length_stacked_label = "Less Than 1 Year,1-3 Years,4-6 Years,More than 6 years"
#                 org_type_stacked_count = get_stacked_counted_list(choice.content, org_type_stacked_label, quest.id,
#                                                                   computed_answers)
#                 org_size_stacked_count = get_stacked_counted_list(choice.content, org_size_stacked_label, quest.id,
#                                                                   computed_answers)
#                 applied_length_stacked_count = get_stacked_counted_list(choice.content, applied_length_stacked_label,
#                                                                         quest.id, computed_answers)
#                 question_dict["org_type_stacked_count"] = org_type_stacked_count
#                 question_dict["org_size_stacked_count"] = org_size_stacked_count
#                 question_dict["applied_length_stacked_count"] = applied_length_stacked_count
#                 question_dict["org_type_stacked_label"] = org_type_stacked_label
#                 question_dict["org_size_stacked_label"] = org_size_stacked_label
#                 question_dict["applied_length_stacked_label"] = applied_length_stacked_label
#
#             question_list.append(question_dict.copy())
#
#     data = {"number_of_completed_survey": completed_answers_users.count(),
#             "number_of_participant": all_answers_users.count(),
#             "number_of_effective_participant": effective_answers_users.count(),
#             "question_list": question_list}
#     return render(request, 'dashboard_summary_stacked_chart.html', data)


def get_all_answer_by_question_id(all_answers, question_id):
    return list(all_answers.filter(question_id=question_id).values_list('content', flat=True))


def count_choice_answer(choice, answer_list):
    choiceList = choice.split(";")
    countList = []
    for choice in choiceList:
        countList.append(sum(map(lambda ans: ans.startswith(choice), answer_list)))

    return countList


def count_multi_choice_answer(choice, answer_list):
    choiceList = choice.split(";")

    answer_list = list(map(lambda answer: answer.split(';;;'), answer_list))
    answer_list = [item for sublist in answer_list for item in sublist]

    countList = []
    for choice in choiceList:
        countList.append(sum(map(lambda ans: ans.startswith(choice), answer_list)))

    return countList


def count_agree_rate(answer_list):
    agree_rate = 0
    count = 0
    for ans in answer_list:
        if ans == "Strongly Agree":
            agree_rate += 4
        if ans == "Agree":
            agree_rate += 3
        if ans == "Disagree":
            agree_rate += 2
        if ans == "Strongly Disagree":
            agree_rate += 1
        if ans == "Strongly Agree" or ans == "Agree" or ans == "Disagree" or ans == "Strongly Disagree":
            count += 1

    return round(agree_rate / count, 3) if agree_rate else None


@login_required
def construct_export(request):
    if not request.user.is_staff:
        return redirect('profile')
    data = {}
    return render(request, 'dashboard_export.html', data)


@login_required
def export_to_xls(request):
    if not request.user.is_staff:
        return redirect('profile')
    buffer = io.BytesIO()

    question_list = get_all_question_in_survey("covid")
    # add first 3 rows
    quesion_id_list_row = [""]
    quesion_id_list = []
    quesion_content_list = [""]
    quesion_type_list = [""]
    for q in question_list:
        quesion_id_list_row.append(q.id)
        quesion_id_list.append(q.id)
        quesion_content_list.append(q.content)
        quesion_type_list.append(q.type)

    quesion_id_list_row.append("isComplete")
    rows = [quesion_id_list_row, quesion_content_list, quesion_type_list]

    # tmp_dict = {"Strongly Agree": 4, "Agree": 3, "Disagree": 2, "Strongly Disagree": 1}
    users = SurveyUser.objects.exclude(last_survey_save__isnull=True).values()
    for user in list(users):
        row = [user.get("id")]
        answers = Answer.objects.filter(user_id=user.get("id")).values()
        answers = list(answers)
        for question_id in quesion_id_list:
            answer = list(filter(lambda dic: dic['question_id'] == question_id, answers))
            row.append(answer[0].get('content') if answer else "")
        row.append(1 if user.get("is_survey_complete") else 0)
        rows.append(row)
    df = pd.DataFrame(rows)

    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    df.to_excel(writer, sheet_name="output", index=False, header=None)
    writer.save()

    # build pdf
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='output-' + strftime("%Y-%m-%d %H:%M", gmtime()) + '.xlsx')


@login_required
def export_text(request):
    if not request.user.is_staff:
        return redirect('profile')

    question_id = request.GET.get('qid')

    all_answers = get_all_answers()
    filename = "all-text-answers-raw.txt"
    content = ''

    sections = get_all_sections()
    for section in sections:
        for quest in section.get_question_in_section():
            if question_id and question_id != str(quest.id):
                continue
            answer_list = get_all_answer_by_question_id(all_answers, quest.id)
            # if quest.type == "text" or quest.type == "choice" or quest.type == "choice-text":
            content += "\n====================\n"
            content += "Question " + str(quest.id) + ": " + str(quest.content) + "\n"
            content += "Type: " + str(quest.type) + "\n"
            content += "Number of answers: " + str(len(answer_list)) + "\n--------------------\n"
            answer_string = "\n--------------------\n".join(answer_list)
            content += answer_string
            if question_id and question_id == str(quest.id):
                filename = str(quest.id) + "-text-answers-raw.txt"
                break

    if content == '':
        content = "no text responses for this question"

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


def get_all_question_id_list_in_survey(survey_slug):
    question_id_list = []
    sections = get_all_sections()
    for section in sections:
        questions = section.get_question_in_section()
        for question in questions:
            question_id_list.append(question.id)
    return question_id_list


def write_row_to_excel(sheet, row_num, col_start, list, style):
    for col_num in range(len(list)):
        sheet.write(row_num, col_num + col_start, list[col_num], style)


def get_all_answers():
    all_answers = Answer.objects.exclude(content__isnull=True).exclude(content__exact='')
    return all_answers


def get_all_answers_users():
    all_answers_users = Answer.objects.exclude(content__isnull=True).exclude(content__exact=''). \
        values('user_id').annotate(answered_total=Count('user_id')).order_by()
    return all_answers_users


def get_effective_answers_users(all_answers_users):
    return all_answers_users.filter(answered_total__gte=19)


def get_all_sections():
    survey = Survey.objects.get(id=1)
    sections = survey.section.order_by("order")
    return sections


def sample_filter(sample, all_answers, all_answers_users, effective_answers_users, completed_answers_users):
    if sample == "effective":
        computed_answers = all_answers.filter(user_id__in=effective_answers_users.values('user_id'))
        computed_answers_users = effective_answers_users
    elif sample == "completed":
        computed_answers = all_answers.filter(user_id__in=completed_answers_users.values('id'))
        computed_answers_users = completed_answers_users
    else:
        computed_answers = all_answers
        computed_answers_users = all_answers_users

    return dict({"computed_answers": computed_answers,
                 "computed_answers_users": computed_answers_users})
