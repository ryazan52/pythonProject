from django import template

register = template.Library()

BAD_WORDS = {
    'Фигня': 'Ф****',
    'фигня': 'ф****',
    'Попа': 'П***',
    'попа': 'п***',
    'Редиска': 'Р******',
    'редиска': 'р******',
    'Ерунда': 'Е*****',
    'ерунда': 'е*****',
}


@register.filter()
def censor(value: str):
    words = value.split(' ')
    new_text = ''

    for i in range(len(words)):
        if words[i] in BAD_WORDS:
            words[i] = BAD_WORDS[words[i]]
            new_text += words[i]
            new_text += ' '
        else:
            new_text += words[i]
            new_text += ' '

    return new_text
