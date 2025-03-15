from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

@login_required
def finance_home(request):
    """Finans ana sayfası"""
    context = {}
    return render(request, 'finance/home.html', context)

@login_required
def payment_list(request):
    """Ödeme listesi görüntüleme"""
    # ödeme listesi
    context = {
        'payments': [],
    }
    return render(request, 'finance/payment_list.html', context)

@login_required
def expense_list(request):
    """Gider listesi görüntüleme"""
    # gider listesi 
    context = {
        'expenses': [],
    }
    return render(request, 'finance/expense_list.html', context)

@login_required
def financial_report(request):
    """Finansal rapor görüntüleme"""
    # finansal
    context = {
        'income_total': 0,
        'expense_total': 0,
        'profit': 0,
    }
    return render(request, 'finance/financial_report.html', context)
