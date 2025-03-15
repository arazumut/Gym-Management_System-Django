from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_home, name='home'),
    # Diğer URL'ler buraya eklenecek
] 