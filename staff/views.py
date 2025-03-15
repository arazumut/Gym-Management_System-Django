from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Department, StaffProfile, Attendance, Leave, Shift, ShiftAssignment, Performance, Payroll
from .forms import (
    StaffProfileForm, AttendanceForm, LeaveRequestForm, ShiftAssignmentForm,
    PerformanceForm, PayrollForm, DepartmentForm
)

@login_required
def staff_home(request):
    """Personel ana sayfası"""
    # Kullanıcının personel profilini kontrol et
    try:
        staff_profile = request.user.staff_profile
    except StaffProfile.DoesNotExist:
        messages.warning(request, _('Personel profiliniz bulunmamaktadır.'))
        return redirect('home')
    
    # Bugünkü devam durumunu kontrol et
    today = timezone.now().date()
    try:
        attendance = Attendance.objects.get(staff=request.user, date=today)
    except Attendance.DoesNotExist:
        attendance = None
    
    # Bekleyen izin taleplerini al
    pending_leaves = Leave.objects.filter(staff=request.user, status='pending')
    
    # Bugünkü vardiyayı al
    try:
        shift_assignment = ShiftAssignment.objects.get(staff=request.user, date=today)
    except ShiftAssignment.DoesNotExist:
        shift_assignment = None
    
    # Son performans değerlendirmesini al
    latest_performance = Performance.objects.filter(staff=request.user).order_by('-review_date').first()
    
    # Son maaş bordrosunu al
    latest_payroll = Payroll.objects.filter(staff=request.user).order_by('-period_end').first()
    
    context = {
        'staff_profile': staff_profile,
        'attendance': attendance,
        'pending_leaves': pending_leaves,
        'shift_assignment': shift_assignment,
        'latest_performance': latest_performance,
        'latest_payroll': latest_payroll,
    }
    
    return render(request, 'staff/home.html', context)

@login_required
def department_list(request):
    """Departman listesi"""
    departments = Department.objects.filter(is_active=True)
    
    # Arama işlemi
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'staff/department_list.html', context)

@login_required
def department_detail(request, pk):
    """Departman detayı"""
    department = get_object_or_404(Department, pk=pk, is_active=True)
    staff_members = StaffProfile.objects.filter(department=department, is_active=True)
    
    context = {
        'department': department,
        'staff_members': staff_members,
    }
    
    return render(request, 'staff/department_detail.html', context)

@login_required
def staff_profile(request):
    """Personel profili"""
    try:
        staff_profile = request.user.staff_profile
    except StaffProfile.DoesNotExist:
        messages.warning(request, _('Personel profiliniz bulunmamaktadır.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, request.FILES, instance=staff_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profiliniz başarıyla güncellendi.'))
            return redirect('staff:profile')
    else:
        form = StaffProfileForm(instance=staff_profile)
    
    context = {
        'staff_profile': staff_profile,
        'form': form,
    }
    
    return render(request, 'staff/profile.html', context)

@login_required
def attendance_list(request):
    """Devam kayıtları listesi"""
    attendances = Attendance.objects.filter(staff=request.user)
    
    # Tarih filtresi
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        attendances = attendances.filter(date__gte=start_date)
    if end_date:
        attendances = attendances.filter(date__lte=end_date)
    
    # Sayfalama
    paginator = Paginator(attendances, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'staff/attendance_list.html', context)

@login_required
def attendance_check_in(request):
    """Giriş yapma"""
    today = timezone.now().date()
    
    # Bugün için zaten giriş yapılmış mı kontrol et
    try:
        attendance = Attendance.objects.get(staff=request.user, date=today)
        if attendance.check_in:
            messages.warning(request, _('Bugün için zaten giriş yapmışsınız.'))
            return redirect('staff:attendance_list')
    except Attendance.DoesNotExist:
        attendance = Attendance(staff=request.user, date=today)
    
    attendance.check_in = timezone.now().time()
    attendance.status = 'present'
    attendance.save()
    
    messages.success(request, _('Giriş başarıyla kaydedildi.'))
    return redirect('staff:home')

@login_required
def attendance_check_out(request):
    """Çıkış yapma"""
    today = timezone.now().date()
    
    try:
        attendance = Attendance.objects.get(staff=request.user, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, _('Bugün için giriş kaydı bulunamadı.'))
        return redirect('staff:attendance_list')
    
    if not attendance.check_in:
        messages.error(request, _('Giriş yapmadan çıkış yapamazsınız.'))
        return redirect('staff:attendance_list')
    
    if attendance.check_out:
        messages.warning(request, _('Bugün için zaten çıkış yapmışsınız.'))
        return redirect('staff:attendance_list')
    
    attendance.check_out = timezone.now().time()
    attendance.save()
    
    messages.success(request, _('Çıkış başarıyla kaydedildi.'))
    return redirect('staff:home')

@login_required
def leave_list(request):
    """İzin talepleri listesi"""
    leaves = Leave.objects.filter(staff=request.user)
    
    # Durum filtresi
    status = request.GET.get('status')
    if status:
        leaves = leaves.filter(status=status)
    
    # Sayfalama
    paginator = Paginator(leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status,
    }
    
    return render(request, 'staff/leave_list.html', context)

@login_required
def leave_request(request):
    """İzin talebi oluşturma"""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff = request.user
            leave.save()
            messages.success(request, _('İzin talebiniz başarıyla oluşturuldu.'))
            return redirect('staff:leave_list')
    else:
        form = LeaveRequestForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'staff/leave_request.html', context)

@login_required
def leave_detail(request, pk):
    """İzin talebi detayı"""
    leave = get_object_or_404(Leave, pk=pk, staff=request.user)
    
    context = {
        'leave': leave,
    }
    
    return render(request, 'staff/leave_detail.html', context)

@login_required
def shift_list(request):
    """Vardiya listesi"""
    shift_assignments = ShiftAssignment.objects.filter(staff=request.user)
    
    # Tarih filtresi
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        shift_assignments = shift_assignments.filter(date__gte=start_date)
    if end_date:
        shift_assignments = shift_assignments.filter(date__lte=end_date)
    
    # Sayfalama
    paginator = Paginator(shift_assignments, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'staff/shift_list.html', context)

@login_required
def shift_detail(request, pk):
    """Vardiya detayı"""
    shift_assignment = get_object_or_404(ShiftAssignment, pk=pk, staff=request.user)
    
    context = {
        'shift_assignment': shift_assignment,
    }
    
    return render(request, 'staff/shift_detail.html', context)

@login_required
def performance_list(request):
    """Performans değerlendirmeleri listesi"""
    performances = Performance.objects.filter(staff=request.user)
    
    # Sayfalama
    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'staff/performance_list.html', context)

@login_required
def performance_detail(request, pk):
    """Performans değerlendirmesi detayı"""
    performance = get_object_or_404(Performance, pk=pk, staff=request.user)
    
    context = {
        'performance': performance,
    }
    
    return render(request, 'staff/performance_detail.html', context)

@login_required
def payroll_list(request):
    """Maaş bordroları listesi"""
    payrolls = Payroll.objects.filter(staff=request.user)
    
    # Sayfalama
    paginator = Paginator(payrolls, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'staff/payroll_list.html', context)

@login_required
def payroll_detail(request, pk):
    """Maaş bordrosu detayı"""
    payroll = get_object_or_404(Payroll, pk=pk, staff=request.user)
    
    context = {
        'payroll': payroll,
    }
    
    return render(request, 'staff/payroll_detail.html', context)
