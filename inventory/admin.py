from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    InventoryCategory, Supplier, InventoryItem, InventoryTransaction,
    MaintenanceSchedule, MaintenanceLog, EquipmentAssignment
)

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'email', 'phone', 'address')

class InventoryTransactionInline(admin.TabularInline):
    model = InventoryTransaction
    extra = 0
    fields = ('transaction_type', 'quantity', 'transaction_date', 'unit_price', 'total_price', 'created_by')
    readonly_fields = ('transaction_date', 'created_by')
    can_delete = False

class MaintenanceScheduleInline(admin.TabularInline):
    model = MaintenanceSchedule
    extra = 0
    fields = ('title', 'frequency', 'last_maintenance_date', 'next_maintenance_date', 'is_active')
    readonly_fields = ('last_maintenance_date',)

class EquipmentAssignmentInline(admin.TabularInline):
    model = EquipmentAssignment
    extra = 0
    fields = ('assigned_to', 'assigned_by', 'assigned_date', 'status', 'return_date')
    readonly_fields = ('assigned_by',)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sku', 'quantity', 'min_quantity', 'is_low_stock', 'condition', 'is_active')
    list_filter = ('category', 'condition', 'is_active', 'supplier')
    search_fields = ('name', 'sku', 'barcode', 'description', 'location')
    readonly_fields = ('is_low_stock', 'stock_value')
    inlines = [InventoryTransactionInline, MaintenanceScheduleInline, EquipmentAssignmentInline]
    
    fieldsets = (
        (None, {'fields': ('name', 'category', 'description', 'image')}),
        (_('Stok Bilgileri'), {'fields': ('sku', 'barcode', 'quantity', 'min_quantity', 'is_low_stock')}),
        (_('Fiyat ve Tedarikçi'), {'fields': ('unit_price', 'stock_value', 'supplier')}),
        (_('Durum ve Konum'), {'fields': ('condition', 'location', 'is_active')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = _('Düşük Stok')

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'transaction_type', 'quantity', 'transaction_date', 'unit_price', 'total_price', 'created_by')
    list_filter = ('transaction_type', 'transaction_date', 'created_by')
    search_fields = ('item__name', 'item__sku', 'reference_number', 'notes')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('created_by',)
    
    fieldsets = (
        (None, {'fields': ('item', 'transaction_type', 'quantity')}),
        (_('Fiyat Bilgileri'), {'fields': ('unit_price', 'total_price')}),
        (_('İşlem Detayları'), {'fields': ('transaction_date', 'reference_number', 'created_by')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    fields = ('title', 'maintenance_date', 'status', 'cost', 'performed_by')

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('item', 'title', 'frequency', 'last_maintenance_date', 'next_maintenance_date', 'is_active', 'is_overdue')
    list_filter = ('frequency', 'is_active', 'next_maintenance_date')
    search_fields = ('item__name', 'title', 'description', 'notes')
    date_hierarchy = 'next_maintenance_date'
    readonly_fields = ('is_overdue', 'days_until_next_maintenance')
    inlines = [MaintenanceLogInline]
    
    fieldsets = (
        (None, {'fields': ('item', 'title', 'description')}),
        (_('Bakım Zamanlaması'), {'fields': ('frequency', 'last_maintenance_date', 'next_maintenance_date')}),
        (_('Durum'), {'fields': ('is_active', 'is_overdue', 'days_until_next_maintenance')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = _('Gecikmiş')

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'schedule', 'title', 'maintenance_date', 'status', 'cost', 'performed_by', 'created_by')
    list_filter = ('status', 'maintenance_date')
    search_fields = ('item__name', 'title', 'description', 'performed_by', 'notes')
    date_hierarchy = 'maintenance_date'
    readonly_fields = ('created_by',)
    
    fieldsets = (
        (None, {'fields': ('schedule', 'item', 'title', 'description')}),
        (_('Bakım Detayları'), {'fields': ('maintenance_date', 'status', 'cost', 'performed_by')}),
        (_('Diğer Bilgiler'), {'fields': ('notes', 'created_by')}),
    )

@admin.register(EquipmentAssignment)
class EquipmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('item', 'assigned_to', 'assigned_by', 'assigned_date', 'expected_return_date', 'return_date', 'status', 'is_overdue')
    list_filter = ('status', 'assigned_date', 'return_date')
    search_fields = ('item__name', 'assigned_to__first_name', 'assigned_to__last_name', 'assigned_to__email', 'notes')
    date_hierarchy = 'assigned_date'
    readonly_fields = ('is_overdue', 'days_overdue')
    
    fieldsets = (
        (None, {'fields': ('item', 'assigned_to', 'assigned_by')}),
        (_('Zimmet Detayları'), {'fields': ('assigned_date', 'expected_return_date', 'return_date', 'status')}),
        (_('Durum Bilgileri'), {'fields': ('condition_on_assignment', 'condition_on_return')}),
        (_('Takip'), {'fields': ('is_overdue', 'days_overdue')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = _('Gecikmiş')
