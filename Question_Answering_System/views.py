from django.shortcuts import render


def questionAnswer(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'questionAnswer.html', context)