
from django.urls import path
from .views import LendingView, MaterialView, download_file

urlpatterns = [
    path('', LendingView.as_view(), name='index'),
    path('materials/', MaterialView.as_view(), name='message'),
    path('download/<str:link>', download_file, name='download'),
]

