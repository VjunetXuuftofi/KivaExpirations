from django.http import HttpResponse
from django.template import loader
from .apps import Data


def display_predictions(request, loanid):
    context = Data.do_everything(loanid)
    template = loader.get_template('predictions.html')
    return HttpResponse(template.render(context, request))


def get_choice(request):
    template = loader.get_template('choice.html')
    return HttpResponse(template.render({}, request))