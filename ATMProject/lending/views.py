import os

from dotenv import load_dotenv
from fast_bitrix24 import Bitrix
from urllib.parse import urlparse

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.views.generic import TemplateView

from .forms import InfoForm
from .models import Info

load_dotenv()


class LendingView(TemplateView):
    template_name = 'lending/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = self.request.session.pop('message', None)
        return context

    def post(self, request, *args, **kwargs):
        form = InfoForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not Info.objects.filter(email=email).exists():
                form.save()
            message = 'Заявка передана успешно!'

            model_obj = Info.objects.get(email=form.data['email'])

            send_mail_form(request, model_obj)

            create_lead(model_obj, 'Заполнение формы лендинг УЦ "АТМ"')

        else:
            message = 'Ошибка при заполнении формы. Пожалуйста, проверьте данные и попробуйте снова.'

        request.session['message'] = message
        return self.render_to_response(self.get_context_data())


class MaterialView(TemplateView):
    template_name = 'lending/material.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = self.request.session.pop('message', None)
        return context

    def post(self, request, *args, **kwargs):
        form = InfoForm(request.POST)
        if form.is_valid():
            if not Info.objects.filter(email=form.data['email']).exists():
                form.save()

            model_obj = Info.objects.get(email=form.data['email'])

            send_mail_form(request, model_obj)

            create_lead(model_obj, 'Заполнение формы получения материалов УЦ "АТМ"')

            message = 'Ссылка отправлена на ваш Email!'
        else:
            message = 'Ошибка при заполнении формы. Пожалуйста, проверьте данные и попробуйте снова.'

        request.session['message'] = message
        return self.render_to_response(self.get_context_data())


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


def create_lead(info, title_lead):
    # разбиваем и устанавливаем имя
    parts = info.fio.split()

    info_last_name = parts[0] if len(parts) > 0 else ''
    info_name = parts[1] if len(parts) > 1 else ''
    info_second_name = parts[2] if len(parts) > 2 else ''

    # ID ответственного
    user_id = 3706

    fields = {
        'TITLE': title_lead,
        'NAME': info_name,
        'LAST_NAME': info_last_name,
        'SECOND_NAME': info_second_name,
        'PHONE': info.phone,
        'EMAIL': info.email,
        'COMPANY_TITLE': info.company,
        'ASSIGNED_BY_ID': user_id
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

    base_url = f"https://{url_parts.netloc}"
    return base_url


def download_file(request, link):
    get_object_or_404(Info, link=link)

    return render(request, f'lending/download.html', context={
        'MEDIA_URL': settings.MEDIA_URL
    })
