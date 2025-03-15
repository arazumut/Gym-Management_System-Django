from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    ClassCategory, ClassRoom, ClassTemplate, ClassSchedule, 
    ClassSession, ClassParticipant, ClassWaitingList
)

@admin.register(ClassCategory)
class ClassCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_active')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'location', 'description')

@admin.register(ClassTemplate)
class ClassTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'difficulty', 'is_active')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('name', 'description', 'benefits', 'requirements')

class ClassSessionInline(admin.TabularInline):
    model = ClassSession
    extra = 1
    fields = ('date', 'start_time', 'end_time', 'instructor', 'room', 'status')

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_template', 'instructor', 'room', 'weekday', 'start_time', 'end_time', 'max_participants', 'is_active')
    list_filter = ('weekday', 'is_active', 'recurrence')
    search_fields = ('class_template__name', 'instructor__first_name', 'instructor__last_name', 'room__name')
    date_hierarchy = 'start_date'
    inlines = [ClassSessionInline]
    
    fieldsets = (
        (None, {'fields': ('class_template', 'instructor', 'room')}),
        (_('Zamanlama'), {'fields': ('start_date', 'end_date', 'weekday', 'start_time', 'end_time', 'recurrence')}),
        (_('Kapasite'), {'fields': ('max_participants',)}),
        (_('Durum'), {'fields': ('is_active',)}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

class ClassParticipantInline(admin.TabularInline):
    model = ClassParticipant
    extra = 1
    fields = ('member', 'attendance_status', 'check_in_time')

class ClassWaitingListInline(admin.TabularInline):
    model = ClassWaitingList
    extra = 1
    fields = ('member', 'registration_time', 'is_active')

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('class_schedule', 'date', 'start_time', 'end_time', 'instructor', 'room', 'status', 'participant_count', 'has_availability')
    list_filter = ('status', 'date', 'instructor')
    search_fields = ('class_schedule__class_template__name', 'instructor__first_name', 'instructor__last_name')
    date_hierarchy = 'date'
    inlines = [ClassParticipantInline, ClassWaitingListInline]
    
    fieldsets = (
        (None, {'fields': ('class_schedule', 'instructor', 'room')}),
        (_('Zamanlama'), {'fields': ('date', 'start_time', 'end_time')}),
        (_('Durum'), {'fields': ('status',)}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
    
    readonly_fields = ('duration_minutes', 'is_past', 'participant_count', 'has_availability')

@admin.register(ClassParticipant)
class ClassParticipantAdmin(admin.ModelAdmin):
    list_display = ('member', 'class_session', 'attendance_status', 'registration_time', 'check_in_time', 'is_checked_in')
    list_filter = ('attendance_status', 'registration_time')
    search_fields = ('member__first_name', 'member__last_name', 'class_session__class_schedule__class_template__name')
    date_hierarchy = 'registration_time'
    
    readonly_fields = ('is_checked_in',)

@admin.register(ClassWaitingList)
class ClassWaitingListAdmin(admin.ModelAdmin):
    list_display = ('member', 'class_session', 'registration_time', 'is_active')
    list_filter = ('is_active', 'registration_time')
    search_fields = ('member__first_name', 'member__last_name', 'class_session__class_schedule__class_template__name')
    date_hierarchy = 'registration_time'
