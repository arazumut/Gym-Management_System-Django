from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_home, name='home'),
    # Diğer URL'ler buraya eklenecek
] 