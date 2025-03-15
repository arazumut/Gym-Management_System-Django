from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def inventory_home(request):
    """Envanter ana sayfası"""
    context = {}
    return render(request, 'inventory/home.html', context)
