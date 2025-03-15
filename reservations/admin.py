from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    ReservableArea, AreaAvailability, AreaReservation,
    EquipmentCategory, Equipment, EquipmentReservation
)

class AreaAvailabilityInline(admin.TabularInline):
    model = AreaAvailability
    extra = 1

@admin.register(ReservableArea)
class ReservableAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_type', 'location', 'capacity', 'price_per_hour', 'is_active')
    list_filter = ('area_type', 'location', 'is_active')
    search_fields = ('name', 'location', 'description')
    inlines = [AreaAvailabilityInline]

@admin.register(AreaAvailability)
class AreaAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('area', 'weekday', 'start_time', 'end_time', 'is_available')
    list_filter = ('weekday', 'is_available')
    search_fields = ('area__name', 'notes')

@admin.register(AreaReservation)
class AreaReservationAdmin(admin.ModelAdmin):
    list_display = ('area', 'member', 'date', 'start_time', 'end_time', 'status', 'number_of_people', 'price', 'is_paid', 'is_past')
    list_filter = ('status', 'is_paid', 'date')
    search_fields = ('area__name', 'member__first_name', 'member__last_name', 'member__email')
    date_hierarchy = 'date'
    readonly_fields = ('duration_hours', 'is_past')
    
    fieldsets = (
        (None, {'fields': ('area', 'member')}),
        (_('Rezervasyon Detayları'), {'fields': ('date', 'start_time', 'end_time', 'number_of_people')}),
        (_('Ödeme Bilgileri'), {'fields': ('price', 'is_paid', 'payment_date')}),
        (_('Durum'), {'fields': ('status', 'is_past', 'duration_hours')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'available_quantity', 'price_per_hour', 'is_reservable', 'is_active', 'is_available')
    list_filter = ('category', 'is_reservable', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('is_available',)

@admin.register(EquipmentReservation)
class EquipmentReservationAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'member', 'quantity', 'date', 'start_time', 'end_time', 'status', 'price', 'is_paid', 'is_past')
    list_filter = ('status', 'is_paid', 'date')
    search_fields = ('equipment__name', 'member__first_name', 'member__last_name', 'member__email')
    date_hierarchy = 'date'
    readonly_fields = ('duration_hours', 'is_past')
    
    fieldsets = (
        (None, {'fields': ('equipment', 'member', 'quantity')}),
        (_('Rezervasyon Detayları'), {'fields': ('date', 'start_time', 'end_time')}),
        (_('Ödeme Bilgileri'), {'fields': ('price', 'is_paid', 'payment_date')}),
        (_('Durum'), {'fields': ('status', 'is_past', 'duration_hours', 'checkout_time', 'return_time')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
