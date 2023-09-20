
from django.urls import path
from .views import get_lending, get_message, download_zip_file

urlpatterns = [
    path('', get_lending, name='index'),
    path('message/', get_message, name='message'),
    path('download/<str:link>', download_zip_file, name='download'),
]

