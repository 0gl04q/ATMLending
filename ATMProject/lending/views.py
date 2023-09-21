import os

from fast_bitrix24 import Bitrix

from django.shortcuts import render, get_object_or_404, redirect, reverse
from urllib.parse import urlparse, urlunparse
from django.core.mail import send_mail
from django.template.loader import get_template
from dotenv import load_dotenv

from .forms import InfoForm
from .models import Info

load_dotenv()


def get_lending(request):
    success_message = None
    if request.method == 'POST':
        form = InfoForm(request.POST)
        if form.is_valid():
            if not Info.objects.filter(email=form.data['email']).exists():
                form.save()
            success_message = 'Заявка передана успешно!'
    return render(request, 'lending/index.html', context={'message': success_message})


def get_message(request):
    success_message = None
    if request.method == 'POST':
        form = InfoForm(request.POST)
        if form.is_valid():
            if not Info.objects.filter(email=form.data['email']).exists():
                form.save()

            model_obj = Info.objects.get(email=form.data['email'])

            # Отправка письма
            send_mail_form(request, model_obj)

            # Отправка лида B24
            create_lead(model_obj)

            success_message = 'Ссылка отправлена на ваш Email!'

    return render(request, 'lending/message.html', context={'message': success_message})


def send_mail_form(request, obj_info):
    mail = os.getenv('HOST_USER')
    send_mail(
        'Доступ к материалам',
        'message',
        mail,
        [obj_info.email],
        fail_silently=False,
        html_message=get_template('lending/confirmation.html').render({
            'obj_info': obj_info,
            'media_url': f"{get_server_url(request)}{reverse('download', args=(obj_info.link,))}"
        })
    )


def create_lead(info):

    # разбиваем и устанавливаем имя
    parts = info.fio.split()

    info_last_name = parts[0] if len(parts) > 0 else ''
    info_name = parts[1] if len(parts) > 1 else ''
    info_second_name = parts[2] if len(parts) > 2 else ''

    # ID ответственного
    user_id = 3706

    fields = {
        'TITLE': 'Заполнение формы получения материалов УЦ "АТМ"',
        'NAME': info_name,
        'LAST_NAME': info_last_name,
        'SECOND_NAME': info_second_name,
        'PHONE': info.phone,
        'EMAIL': info.email,
        'COMPANY_TITLE': info.company,
        'ASSIGNED_BY_ID': 3706
    }

    lead = {
        'fields': {
            'TITLE': fields['TITLE'],
            'ASSIGNED_BY_ID': fields['ASSIGNED_BY_ID']
        }
    }

    contact = {
        'fields': {
            'NAME': fields['NAME'],
            'LAST_NAME': fields['LAST_NAME'],
            'SECOND_NAME': fields['SECOND_NAME'],
            'PHONE': [{'VALUE': fields['PHONE'], 'VALUE_TYPE': 'WORK'}],
            'EMAIL': [{'VALUE': fields['EMAIL'], 'VALUE_TYPE': 'WORK'}],
            'COMPANY_TITLE': fields['COMPANY_TITLE']
        }
    }

    b = Bitrix('https://atm-2016.bitrix24.ru/rest/1570/l0fyq12d2jfqnjzh/')
    with b.slow():
        result = b.call('crm.contact.add', contact)

        lead['fields']['CONTACT_ID'] = result

        b.call('crm.lead.add', lead)


def get_server_url(request):
    current_url = request.build_absolute_uri()
    url_parts = urlparse(current_url)
    server_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return server_url


def download_zip_file(request, link):
    get_object_or_404(Info, link=link)
    return redirect('/media/Материалы.zip')
