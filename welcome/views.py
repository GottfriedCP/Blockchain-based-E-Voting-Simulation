from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    context = {
        'tx': settings.N_TRANSACTIONS,
        'bl': settings.N_BLOCKS,
    }
    return render(request, 'welcome/home.html', context)
