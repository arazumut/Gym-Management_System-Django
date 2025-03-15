from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.trainer_home, name='home'),
    # Diğer URL'ler buraya eklenecek
] 