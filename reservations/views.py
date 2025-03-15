from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def reservation_home(request):
    """Rezervasyonlar ana sayfası"""
    context = {}
    return render(request, 'reservations/home.html', context)
