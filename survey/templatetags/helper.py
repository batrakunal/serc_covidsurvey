from django import template
import re

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_answer(answers, choice):
    answers_list = answers.split(';;;')
    for answer in answers_list:
        match = re.search(r"^(\[.+\])(.*)$", answer)
        if match and match.group(1) == choice:
            return answer
        elif answer == choice:
            return answer
    return None


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def is_text_choice(choice):
    if re.match(r"^\[.+\]$", choice):
        return True
    return False


@register.filter
def remove_bracket(choice):
    return choice.strip("[]")


@register.filter
def get_answer_content(answer):
    match = re.search(r"^(\[.+\])(.*)$", answer)
    if match:
        return match.group(2)
    return ""


@register.filter
def get_answer_choice(answer):
    match = re.search(r"^(\[.+\])(.*)$", answer)
    if match:
        return match.group(1)
    return ""


@register.filter
def get_matrix_degree(choices):
    return choices[0].strip('{}').split(',')


@register.filter
def match_matrix_text_answer_choice(answers, choice):
    answers_list = answers.split(';;;')
    for answer in answers_list:
        match = re.search(r"^(\[\[.+\]\])(.*)$", answer)
        if match and match.group(1) == "[" + choice + "]":
            return answer
    return None


@register.filter
def get_matrix_text_answer_content(answer):
    match = re.search(r"^(\[\[.+\]\])(.*)$", answer)
    if match:
        return match.group(2)
    return ""


@register.filter
def match_matrix_radio_answer_choice(answers, choice):
    answers_list = answers.split(';;;')
    for answer in answers_list:
        match = re.search(r"^(\[.+\])(.*)$", answer)
        if match and match.group(1) == "[" + choice + "]":
            return answer
    return None


@register.filter
def match_matrix_radio_answer_degree(answers, degree):
    answers_list = answers.split(';;;')
    for answer in answers_list:
        match = re.search(r"^(\[.+\])(.*)$", answer)
        if match and match.group(2) == degree:
            return answer
    return None


@register.filter
def split_answer(answers):
    return answers.split(';;;')


@register.filter
def add_space_between_choice_answer(answer):
    search_result = re.search(r'\]([^\]]|$)', answer)
    if search_result:
        return answer[:search_result.start() + 1] + " " + answer[search_result.start() + 1:]
    return answer
