from django.forms import ModelForm
from .models import Info


class InfoForm(ModelForm):
    class Meta:
        model = Info
        fields = ['fio', 'phone', 'company', 'email']
        labels = {
            'fio': 'ФИО',
            'phone': 'Телефон',
            'email': 'Email'
        }