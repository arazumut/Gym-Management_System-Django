from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    PaymentMethod, Transaction, MembershipPayment, 
    Invoice, InvoiceItem, Expense, FinancialReport
)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_type', 'is_active')
    list_filter = ('payment_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'amount', 'payment_method', 'status', 'transaction_date', 'created_by')
    list_filter = ('transaction_type', 'status', 'payment_method', 'transaction_date')
    search_fields = ('transaction_id', 'description', 'reference_number', 'notes')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('transaction_id',)
    
    fieldsets = (
        (None, {'fields': ('transaction_id', 'transaction_type', 'amount', 'description')}),
        (_('Ödeme Bilgileri'), {'fields': ('payment_method', 'status', 'transaction_date', 'reference_number')}),
        (_('Diğer Bilgiler'), {'fields': ('notes', 'created_by')}),
    )

@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'membership', 'amount', 'payment_date', 'transaction')
    list_filter = ('payment_date',)
    search_fields = ('member__first_name', 'member__last_name', 'member__email', 'notes')
    date_hierarchy = 'payment_date'

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'tax_rate', 'discount_rate', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount')
    readonly_fields = ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'member', 'issue_date', 'due_date', 'status', 'total_amount', 'is_paid', 'is_overdue')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'member__first_name', 'member__last_name', 'member__email', 'notes')
    date_hierarchy = 'issue_date'
    readonly_fields = ('invoice_number', 'is_paid', 'is_overdue')
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        (None, {'fields': ('invoice_number', 'member', 'created_by')}),
        (_('Tarihler'), {'fields': ('issue_date', 'due_date')}),
        (_('Tutarlar'), {'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')}),
        (_('Durum'), {'fields': ('status', 'is_paid', 'is_overdue')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'tax_rate', 'discount_rate', 'total_amount')
    list_filter = ('invoice__status',)
    search_fields = ('description', 'invoice__invoice_number')
    readonly_fields = ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_category', 'amount', 'expense_date', 'payment_due_date', 'status', 'is_paid', 'is_overdue', 'created_by')
    list_filter = ('expense_category', 'status', 'expense_date')
    search_fields = ('description', 'notes')
    date_hierarchy = 'expense_date'
    readonly_fields = ('is_paid', 'is_overdue')
    
    fieldsets = (
        (None, {'fields': ('expense_category', 'description', 'amount')}),
        (_('Tarihler'), {'fields': ('expense_date', 'payment_due_date', 'payment_date')}),
        (_('Ödeme Bilgileri'), {'fields': ('status', 'payment_method', 'transaction', 'receipt')}),
        (_('Durum'), {'fields': ('is_paid', 'is_overdue')}),
        (_('Diğer Bilgiler'), {'fields': ('notes', 'created_by', 'approved_by')}),
    )

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'start_date', 'end_date', 'total_income', 'total_expense', 'net_profit', 'generated_by')
    list_filter = ('report_type', 'start_date', 'end_date')
    search_fields = ('title', 'notes')
    date_hierarchy = 'end_date'
    readonly_fields = ('net_profit',)
    
    fieldsets = (
        (None, {'fields': ('report_type', 'title', 'start_date', 'end_date')}),
        (_('Finansal Özet'), {'fields': ('total_income', 'total_expense', 'net_profit')}),
        (_('Rapor Detayları'), {'fields': ('report_data', 'notes', 'generated_by')}),
    )
