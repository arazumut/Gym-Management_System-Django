from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def member_home(request):
    """Üye ana sayfası"""
    context = {}
    return render(request, 'members/home.html', context)
