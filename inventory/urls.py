from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_home, name='home'),
    # Diğer URL'ler buraya eklenecek
] 