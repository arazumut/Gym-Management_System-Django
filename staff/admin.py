from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Department, StaffProfile, Attendance, Leave, Shift, ShiftAssignment, Performance, Payroll

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('staff', 'department', 'position', 'employment_type', 'hire_date', 'salary', 'is_active')
    list_filter = ('department', 'employment_type', 'is_active', 'hire_date')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'position')
    date_hierarchy = 'hire_date'
    readonly_fields = ('employment_duration',)
    
    fieldsets = (
        (None, {'fields': ('staff', 'department', 'position', 'employment_type')}),
        (_('İstihdam Bilgileri'), {'fields': ('hire_date', 'end_date', 'salary', 'is_active', 'employment_duration')}),
        (_('Kişisel Bilgiler'), {'fields': ('emergency_contact_name', 'emergency_contact_phone')}),
        (_('Finansal Bilgiler'), {'fields': ('bank_account', 'tax_id', 'social_security_number')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'check_in', 'check_out', 'status', 'duration')
    list_filter = ('status', 'date')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('duration',)

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'leave_type', 'start_date', 'end_date', 'status', 'days', 'is_approved')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'reason', 'notes')
    date_hierarchy = 'start_date'
    readonly_fields = ('days', 'is_approved')
    
    fieldsets = (
        (None, {'fields': ('staff', 'leave_type')}),
        (_('Tarihler'), {'fields': ('start_date', 'end_date', 'days')}),
        (_('Durum'), {'fields': ('status', 'is_approved', 'approved_by', 'approved_date')}),
        (_('Detaylar'), {'fields': ('reason', 'notes')}),
    )

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'duration_hours', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('duration_hours',)

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('staff', 'shift', 'date')
    list_filter = ('shift', 'date')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'shift__name')
    date_hierarchy = 'date'

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'reviewer', 'review_date', 'overall_rating', 'average_rating')
    list_filter = ('review_date', 'overall_rating')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'reviewer__first_name', 'reviewer__last_name')
    date_hierarchy = 'review_date'
    readonly_fields = ('average_rating',)
    
    fieldsets = (
        (None, {'fields': ('staff', 'reviewer', 'review_date')}),
        (_('Değerlendirme Dönemi'), {'fields': ('period_start', 'period_end')}),
        (_('Puanlar'), {'fields': (
            'punctuality_rating', 'attendance_rating', 'productivity_rating',
            'quality_rating', 'teamwork_rating', 'communication_rating',
            'overall_rating', 'average_rating'
        )}),
        (_('Değerlendirme'), {'fields': ('strengths', 'areas_for_improvement', 'goals', 'comments')}),
    )

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('staff', 'period_start', 'period_end', 'basic_salary', 'overtime_amount', 'net_salary', 'status')
    list_filter = ('status', 'period_end', 'payment_date')
    search_fields = ('staff__first_name', 'staff__last_name', 'staff__email', 'notes')
    date_hierarchy = 'period_end'
    readonly_fields = ('overtime_amount', 'net_salary')
    
    fieldsets = (
        (None, {'fields': ('staff', 'period_start', 'period_end')}),
        (_('Maaş Detayları'), {'fields': (
            'basic_salary', 'overtime_hours', 'overtime_rate', 'overtime_amount',
            'bonus', 'allowances', 'deductions', 'tax', 'net_salary'
        )}),
        (_('Ödeme Bilgileri'), {'fields': ('payment_date', 'payment_method', 'status')}),
        (_('Onay Bilgileri'), {'fields': ('created_by', 'approved_by')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
