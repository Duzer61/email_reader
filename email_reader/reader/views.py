from config import config as cf
from django.shortcuts import render

from .models import EmailAccount


def index(request):
    email_accounts = EmailAccount.objects.all()
    context = {
        'start_message': cf.START_MESSAGE,
        'email_accounts': email_accounts
    }
    return render(request, 'reader/index.html', context)
