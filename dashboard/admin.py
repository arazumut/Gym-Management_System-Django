from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Announcement, DashboardWidget, UserDashboard, UserDashboardWidget, Report, Notification, Task

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'start_date', 'end_date', 'is_active', 'is_expired', 'created_by')
    list_filter = ('priority', 'is_active', 'start_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_expired',)
    
    fieldsets = (
        (None, {'fields': ('title', 'content', 'priority')}),
        (_('Tarihler'), {'fields': ('start_date', 'end_date', 'is_expired')}),
        (_('Durum'), {'fields': ('is_active', 'created_by')}),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Süresi Doldu')

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'widget_type', 'position', 'size', 'is_active')
    list_filter = ('widget_type', 'is_active', 'size')
    search_fields = ('name', 'description')
    
    fieldsets = (
        (None, {'fields': ('name', 'widget_type', 'description')}),
        (_('Görünüm'), {'fields': ('position', 'size', 'is_active')}),
        (_('Konfigürasyon'), {'fields': ('config',)}),
    )

class UserDashboardWidgetInline(admin.TabularInline):
    model = UserDashboardWidget
    extra = 1
    fields = ('widget', 'position', 'is_visible')

@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'widget_count', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    inlines = [UserDashboardWidgetInline]
    
    def widget_count(self, obj):
        return obj.widgets.count()
    widget_count.short_description = _('Widget Sayısı')

@admin.register(UserDashboardWidget)
class UserDashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('user_dashboard', 'widget', 'position', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('user_dashboard__user__first_name', 'user_dashboard__user__last_name', 'widget__name')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'period', 'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('report_type', 'period', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('name', 'report_type', 'description')}),
        (_('Dönem'), {'fields': ('period', 'start_date', 'end_date')}),
        (_('Parametreler'), {'fields': ('parameters',)}),
        (_('Sonuçlar'), {'fields': ('result_data',)}),
        (_('Oluşturma Bilgileri'), {'fields': ('created_by',)}),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'title', 'message')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('user', 'title', 'message')}),
        (_('Detaylar'), {'fields': ('notification_type', 'link', 'is_read')}),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'priority', 'status', 'due_date', 'is_overdue')
    list_filter = ('priority', 'status', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__first_name', 'assigned_to__last_name', 'assigned_by__first_name', 'assigned_by__last_name')
    date_hierarchy = 'due_date'
    readonly_fields = ('is_overdue',)
    
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        (_('Atama Bilgileri'), {'fields': ('assigned_to', 'assigned_by')}),
        (_('Durum'), {'fields': ('priority', 'status', 'is_overdue')}),
        (_('Tarihler'), {'fields': ('due_date', 'completed_date')}),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = _('Süresi Geçti')
