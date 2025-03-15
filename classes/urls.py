from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_home, name='home'),
    # Diğer URL'ler buraya eklenecek classes için.
]