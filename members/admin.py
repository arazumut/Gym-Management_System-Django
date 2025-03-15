from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MembershipPlan, Membership, MemberMeasurement, CheckInOut

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'plan', 'start_date', 'end_date', 'payment_status', 'is_active', 'is_expired', 'days_left')
    list_filter = ('payment_status', 'is_active', 'plan')
    search_fields = ('member__first_name', 'member__last_name', 'member__email')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_expired', 'days_left', 'days_since_start')
    
    fieldsets = (
        (None, {'fields': ('member', 'plan')}),
        (_('Tarihler'), {'fields': ('start_date', 'end_date')}),
        (_('Ödeme Bilgileri'), {'fields': ('payment_status', 'payment_date', 'amount_paid')}),
        (_('Durum'), {'fields': ('is_active', 'is_expired', 'days_left', 'days_since_start')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

@admin.register(MemberMeasurement)
class MemberMeasurementAdmin(admin.ModelAdmin):
    list_display = ('member', 'date', 'weight', 'height', 'bmi', 'body_fat_percentage')
    list_filter = ('date',)
    search_fields = ('member__first_name', 'member__last_name', 'member__email')
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {'fields': ('member', 'date')}),
        (_('Temel Ölçümler'), {'fields': ('weight', 'height', 'bmi', 'body_fat_percentage', 'muscle_mass')}),
        (_('Vücut Ölçüleri'), {'fields': ('chest', 'waist', 'hips', 'arms', 'thighs')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

@admin.register(CheckInOut)
class CheckInOutAdmin(admin.ModelAdmin):
    list_display = ('member', 'check_in_time', 'check_out_time', 'duration', 'is_checked_out')
    list_filter = ('member', 'check_in_time', 'check_out_time')
    search_fields = ('member__first_name', 'member__last_name', 'member__email')
    date_hierarchy = 'check_in_time'
    readonly_fields = ('duration', 'is_checked_out')
    
    def is_checked_out(self, obj):
        return obj.is_checked_out
    is_checked_out.boolean = True
    is_checked_out.short_description = _('Çıkış Yapıldı')
