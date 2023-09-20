import os

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
            obj_info = Info.objects.get(email=form.data['email'])
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
            success_message = 'Ссылка отправлена на ваш Email!'

    return render(request, 'lending/message.html', context={'message': success_message})


def get_server_url(request):
    current_url = request.build_absolute_uri()
    url_parts = urlparse(current_url)
    server_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return server_url


def download_zip_file(request, link):
    get_object_or_404(Info, link=link)
    return redirect('/media/Материалы.zip')
