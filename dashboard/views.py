from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Avg, Max
from django.core.paginator import Paginator

from .models import Announcement, DashboardWidget, UserDashboard, UserDashboardWidget, Report, Notification, Task
from .forms import (
    AnnouncementForm, DashboardWidgetForm, ReportForm, TaskForm
)

from members.models import Membership, MemberMeasurement, CheckInOut
from finance.models import Transaction, MembershipPayment, Invoice, Expense
from inventory.models import InventoryItem, InventoryTransaction
from classes.models import ClassSession, ClassParticipant
from staff.models import Attendance, Leave, Performance

@login_required
def dashboard_home(request):
    """Dashboard ana sayfası"""
    
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    
    # Kullanıcının widget'larını al
    user_widgets = UserDashboardWidget.objects.filter(
        user_dashboard=user_dashboard,
        is_visible=True
    ).select_related('widget').order_by('position')
    
    announcements = Announcement.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date()
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
    ).order_by('-priority', '-start_date')[:5]
    

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    pending_tasks = Task.objects.filter(
        assigned_to=request.user,
        status__in=['pending', 'in_progress']
    ).order_by('-priority', 'due_date')[:5]
    
    context = {
        'user_dashboard': user_dashboard,
        'user_widgets': user_widgets,
        'announcements': announcements,
        'unread_notifications': unread_notifications,
        'pending_tasks': pending_tasks,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def widget_list(request):
    """Widget listesi"""
    widgets = DashboardWidget.objects.filter(is_active=True)
    
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    
    user_widgets = UserDashboardWidget.objects.filter(
        user_dashboard=user_dashboard
    ).values_list('widget_id', flat=True)
    
    context = {
        'widgets': widgets,
        'user_widgets': user_widgets,
    }
    
    return render(request, 'dashboard/widget_list.html', context)

@login_required
def widget_detail(request, pk):
    """Widget detayı"""
    widget = get_object_or_404(DashboardWidget, pk=pk, is_active=True)
    
    widget_data = get_widget_data(widget)
    
    context = {
        'widget': widget,
        'widget_data': widget_data,
    }
    
    return render(request, 'dashboard/widget_detail.html', context)

@login_required
def widget_add(request):
    """Widget ekleme"""
    widget_id = request.POST.get('widget_id')
    
    if not widget_id:
        messages.error(request, _('Geçersiz widget.'))
        return redirect('dashboard:widget_list')
    
    widget = get_object_or_404(DashboardWidget, pk=widget_id, is_active=True)
    
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    
    if UserDashboardWidget.objects.filter(user_dashboard=user_dashboard, widget=widget).exists():
        messages.warning(request, _('Bu widget zaten eklenmiş.'))
        return redirect('dashboard:widget_list')
    
    last_position = UserDashboardWidget.objects.filter(
        user_dashboard=user_dashboard
    ).aggregate(max_position=Max('position'))['max_position'] or 0
    
    UserDashboardWidget.objects.create(
        user_dashboard=user_dashboard,
        widget=widget,
        position=last_position + 1,
        is_visible=True
    )
    
    messages.success(request, _('Widget başarıyla eklendi.'))
    return redirect('dashboard:home')

@login_required
def widget_edit(request, pk):
    """Widget düzenleme"""
    user_widget = get_object_or_404(
        UserDashboardWidget,
        pk=pk,
        user_dashboard__user=request.user
    )
    
    if request.method == 'POST':
        position = request.POST.get('position')
        is_visible = request.POST.get('is_visible') == 'on'
        
        user_widget.position = position
        user_widget.is_visible = is_visible
        user_widget.save()
        
        messages.success(request, _('Widget başarıyla güncellendi.'))
        return redirect('dashboard:home')
    
    context = {
        'user_widget': user_widget,
    }
    
    return render(request, 'dashboard/widget_edit.html', context)

@login_required
def widget_remove(request, pk):
    """Widget kaldırma"""
    user_widget = get_object_or_404(
        UserDashboardWidget,
        pk=pk,
        user_dashboard__user=request.user
    )
    
    user_widget.delete()
    
    messages.success(request, _('Widget başarıyla kaldırıldı.'))
    return redirect('dashboard:home')

@login_required
def announcement_list(request):
    """Duyuru listesi"""
    announcements = Announcement.objects.all()
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        announcements = announcements.filter(is_active=True)
    elif is_active == 'false':
        announcements = announcements.filter(is_active=False)
    
    search_query = request.GET.get('search', '')
    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_active': is_active,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/announcement_list.html', context)

@login_required
@permission_required('dashboard.add_announcement', raise_exception=True)
def announcement_add(request):
    """Duyuru ekleme"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, _('Duyuru başarıyla oluşturuldu.'))
            return redirect('dashboard:announcement_list')
    else:
        form = AnnouncementForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'dashboard/announcement_form.html', context)

@login_required
def announcement_detail(request, pk):
    """Duyuru detayı"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    context = {
        'announcement': announcement,
    }
    
    return render(request, 'dashboard/announcement_detail.html', context)

@login_required
@permission_required('dashboard.change_announcement', raise_exception=True)
def announcement_edit(request, pk):
    """Duyuru düzenleme"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, _('Duyuru başarıyla güncellendi.'))
            return redirect('dashboard:announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    context = {
        'form': form,
        'announcement': announcement,
    }
    
    return render(request, 'dashboard/announcement_form.html', context)

@login_required
def report_list(request):
    """Rapor listesi"""
    reports = Report.objects.all()
    
    report_type = request.GET.get('report_type')
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    search_query = request.GET.get('search', '')
    if search_query:
        reports = reports.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'report_type': report_type,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/report_list.html', context)

@login_required
@permission_required('dashboard.add_report', raise_exception=True)
def report_generate(request):
    """Rapor oluşturma"""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            
            report_data = generate_report_data(
                report.report_type,
                report.start_date,
                report.end_date,
                report.parameters
            )
            
            report.result_data = report_data
            report.save()
            
            messages.success(request, _('Rapor başarıyla oluşturuldu.'))
            return redirect('dashboard:report_detail', pk=report.pk)
    else:
        form = ReportForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'dashboard/report_form.html', context)

@login_required
def report_detail(request, pk):
    """Rapor detayı"""
    report = get_object_or_404(Report, pk=pk)
    
    context = {
        'report': report,
    }
    
    return render(request, 'dashboard/report_detail.html', context)

@login_required
def notification_list(request):
    """Bildirim listesi"""
    notifications = Notification.objects.filter(user=request.user)
    
    is_read = request.GET.get('is_read')
    if is_read == 'true':
        notifications = notifications.filter(is_read=True)
    elif is_read == 'false':
        notifications = notifications.filter(is_read=False)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_read': is_read,
    }
    
    return render(request, 'dashboard/notification_list.html', context)

@login_required
def notification_mark_read(request):
    """Bildirimleri okundu olarak işaretle"""
    notification_ids = request.POST.getlist('notification_ids')
    
    if notification_ids:
        Notification.objects.filter(
            user=request.user,
            id__in=notification_ids
        ).update(is_read=True)
        
        messages.success(request, _('Bildirimler okundu olarak işaretlendi.'))
    
    return redirect('dashboard:notification_list')

@login_required
def task_list(request):
    """Görev listesi"""

    assigned_tasks = Task.objects.filter(assigned_to=request.user)
    
    created_tasks = Task.objects.filter(assigned_by=request.user)
    
    status = request.GET.get('status')
    if status:
        assigned_tasks = assigned_tasks.filter(status=status)
        created_tasks = created_tasks.filter(status=status)
    
    search_query = request.GET.get('search', '')
    if search_query:
        assigned_tasks = assigned_tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        created_tasks = created_tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    assigned_paginator = Paginator(assigned_tasks, 10)
    assigned_page_number = request.GET.get('assigned_page')
    assigned_page_obj = assigned_paginator.get_page(assigned_page_number)
    
    created_paginator = Paginator(created_tasks, 10)
    created_page_number = request.GET.get('created_page')
    created_page_obj = created_paginator.get_page(created_page_number)
    
    context = {
        'assigned_page_obj': assigned_page_obj,
        'created_page_obj': created_page_obj,
        'status': status,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/task_list.html', context)

@login_required
def task_detail(request, pk):
    """Görev detayı"""
    tasks = Task.objects.filter(Q(assigned_to=request.user) | Q(assigned_by=request.user))
    task = get_object_or_404(tasks, pk=pk)
    
    context = {
        'task': task,
    }
    
    return render(request, 'dashboard/task_detail.html', context)

@login_required
def task_add(request):
    """Görev ekleme"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            
            Notification.objects.create(
                user=task.assigned_to,
                title=_('Yeni Görev'),
                message=_('Size yeni bir görev atandı: {}').format(task.title),
                notification_type='info',
                link=f'/dashboard/tasks/{task.pk}/'
            )
            
            messages.success(request, _('Görev başarıyla oluşturuldu.'))
            return redirect('dashboard:task_list')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'dashboard/task_form.html', context)

@login_required
def task_edit(request, pk):
    """Görev düzenleme"""
    tasks = Task.objects.filter(Q(assigned_to=request.user) | Q(assigned_by=request.user))
    task = get_object_or_404(tasks, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, _('Görev başarıyla güncellendi.'))
            return redirect('dashboard:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
    }
    
    return render(request, 'dashboard/task_form.html', context)

@login_required
def task_complete(request, pk):
    """Görevi tamamla"""
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    if task.status in ['completed', 'cancelled']:
        messages.warning(request, _('Bu görev zaten tamamlanmış veya iptal edilmiş.'))
        return redirect('dashboard:task_detail', pk=task.pk)
    
    task.status = 'completed'
    task.completed_date = timezone.now()
    task.save()
    
    Notification.objects.create(
        user=task.assigned_by,
        title=_('Görev Tamamlandı'),
        message=_('Atadığınız görev tamamlandı: {}').format(task.title),
        notification_type='success',
        link=f'/dashboard/tasks/{task.pk}/'
    )
    
    messages.success(request, _('Görev başarıyla tamamlandı.'))
    return redirect('dashboard:task_list')

def get_widget_data(widget):
    """Widget verilerini al"""
    today = timezone.now().date()
    
    if widget.widget_type == 'members_count':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        total_members = User.objects.filter(role='member').count()
        active_members = User.objects.filter(role='member', is_active=True).count()
        
        return {
            'total_members': total_members,
            'active_members': active_members,
        }
    
    elif widget.widget_type == 'active_memberships':
        active_memberships = Membership.objects.filter(
            is_active=True,
            end_date__gte=today
        ).count()
        
        expiring_soon = Membership.objects.filter(
            is_active=True,
            end_date__range=[today, today + timezone.timedelta(days=30)]
        ).count()
        
        return {
            'active_memberships': active_memberships,
            'expiring_soon': expiring_soon,
        }
    
    elif widget.widget_type == 'revenue_chart':
        months = []
        revenues = []
        
        for i in range(5, -1, -1):
            month_start = (today.replace(day=1) - timezone.timedelta(days=1)).replace(day=1)
            month_start = month_start.replace(month=(month_start.month - i) % 12 or 12)
            
            if month_start.month > today.month:
                month_start = month_start.replace(year=today.year - 1)
            
            month_end = (month_start.replace(month=month_start.month % 12 + 1, day=1) - timezone.timedelta(days=1))
            
            revenue = Transaction.objects.filter(
                transaction_type='income',
                status='completed',
                transaction_date__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            months.append(month_start.strftime('%b %Y'))
            revenues.append(float(revenue))
        
        return {
            'months': months,
            'revenues': revenues,
        }
    
    
    return {}

def generate_report_data(report_type, start_date, end_date, parameters):
    """Rapor verilerini oluştur"""
    if report_type == 'membership':
        new_memberships = Membership.objects.filter(
            start_date__range=[start_date, end_date]
        ).count()
        
        expired_memberships = Membership.objects.filter(
            end_date__range=[start_date, end_date]
        ).count()
        
        active_memberships = Membership.objects.filter(
            is_active=True,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).count()
        
        membership_revenue = MembershipPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return {
            'new_memberships': new_memberships,
            'expired_memberships': expired_memberships,
            'active_memberships': active_memberships,
            'membership_revenue': float(membership_revenue),
        }
    
    elif report_type == 'financial':
        income = Transaction.objects.filter(
            transaction_type='income',
            status='completed',
            transaction_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            transaction_type='expense',
            status='completed',
            transaction_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        net_profit = income - expense
        
        income_categories = {}
        membership_income = MembershipPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        income_categories['membership'] = float(membership_income)
        
         
        
        expense_categories = {}
        for category, _ in Expense.EXPENSE_CATEGORY_CHOICES:
            category_expense = Expense.objects.filter(
                expense_category=category,
                expense_date__range=[start_date, end_date],
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or 0
            expense_categories[category] = float(category_expense)
        
        return {
            'income': float(income),
            'expense': float(expense),
            'net_profit': float(net_profit),
            'income_categories': income_categories,
            'expense_categories': expense_categories,
        }
    
    
    return {}
