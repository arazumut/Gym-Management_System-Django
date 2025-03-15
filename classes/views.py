from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def class_home(request):
    """Dersler ana sayfası"""
    context = {}
    return render(request, 'classes/home.html', context)
