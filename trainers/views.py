from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def trainer_home(request):
    """Eğitmen ana sayfası"""
    context = {}
    return render(request, 'trainers/home.html', context)

# Create your views here.
