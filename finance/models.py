from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import uuid

class PaymentMethod(models.Model):
    """Ödeme yöntemi modeli"""
    
    PAYMENT_TYPE_CHOICES = [
        ('cash', _('Nakit')),
        ('credit_card', _('Kredi Kartı')),
        ('debit_card', _('Banka Kartı')),
        ('bank_transfer', _('Banka Havalesi')),
        ('online_payment', _('Online Ödeme')),
        ('check', _('Çek')),
        ('other', _('Diğer')),
    ]
    
    name = models.CharField(_('Ödeme Yöntemi Adı'), max_length=100)
    payment_type = models.CharField(_('Ödeme Tipi'), max_length=20, choices=PAYMENT_TYPE_CHOICES)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ödeme Yöntemi')
        verbose_name_plural = _('Ödeme Yöntemleri')
    
    def __str__(self):
        return f"{self.name} ({self.get_payment_type_display()})"

class Transaction(models.Model):
    """İşlem modeli"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('income', _('Gelir')),
        ('expense', _('Gider')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('completed', _('Tamamlandı')),
        ('failed', _('Başarısız')),
        ('refunded', _('İade Edildi')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    transaction_id = models.UUIDField(_('İşlem ID'), default=uuid.uuid4, editable=False, unique=True)
    transaction_type = models.CharField(_('İşlem Tipi'), max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    description = models.TextField(_('Açıklama'))
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='transactions')
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_date = models.DateTimeField(_('İşlem Tarihi'), default=timezone.now)
    reference_number = models.CharField(_('Referans Numarası'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_transactions')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İşlem')
        verbose_name_plural = _('İşlemler')
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} TL - {self.transaction_date.strftime('%d/%m/%Y %H:%M')}"

class MembershipPayment(models.Model):
    """Üyelik ödemesi modeli"""
    
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_payments')
    membership = models.ForeignKey('members.Membership', on_delete=models.CASCADE, related_name='payments')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='membership_payment')
    payment_date = models.DateTimeField(_('Ödeme Tarihi'), default=timezone.now)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Üyelik Ödemesi')
        verbose_name_plural = _('Üyelik Ödemeleri')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.amount} TL - {self.payment_date.strftime('%d/%m/%Y %H:%M')}"

class Invoice(models.Model):
    """Fatura modeli"""
    
    STATUS_CHOICES = [
        ('draft', _('Taslak')),
        ('sent', _('Gönderildi')),
        ('paid', _('Ödendi')),
        ('overdue', _('Gecikmiş')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    invoice_number = models.CharField(_('Fatura Numarası'), max_length=50, unique=True)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    issue_date = models.DateField(_('Düzenleme Tarihi'))
    due_date = models.DateField(_('Son Ödeme Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(_('Ara Toplam'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(_('İndirim Tutarı'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_invoices')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Fatura')
        verbose_name_plural = _('Faturalar')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Fatura #{self.invoice_number} - {self.member.get_full_name()} - {self.total_amount} TL"
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Otomatik fatura numarası oluştur
            year = timezone.now().year
            month = timezone.now().month
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{year}{month:02d}"
            ).order_by('invoice_number').last()
            
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.invoice_number = f"INV-{year}{month:02d}-{new_number:04d}"
        
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)

class InvoiceItem(models.Model):
    """Fatura kalemi modeli"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(_('Açıklama'), max_length=255)
    quantity = models.PositiveIntegerField(_('Miktar'), default=1)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('Vergi Oranı (%)'), max_digits=5, decimal_places=2, default=18)
    discount_rate = models.DecimalField(_('İndirim Oranı (%)'), max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('Ara Toplam'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(_('İndirim Tutarı'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Fatura Kalemi')
        verbose_name_plural = _('Fatura Kalemleri')
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price} TL"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.discount_amount = self.subtotal * (self.discount_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)

class Expense(models.Model):
    """Gider modeli"""
    
    EXPENSE_CATEGORY_CHOICES = [
        ('rent', _('Kira')),
        ('utilities', _('Faturalar')),
        ('salaries', _('Maaşlar')),
        ('equipment', _('Ekipman')),
        ('maintenance', _('Bakım')),
        ('marketing', _('Pazarlama')),
        ('insurance', _('Sigorta')),
        ('taxes', _('Vergiler')),
        ('supplies', _('Sarf Malzemeleri')),
        ('other', _('Diğer')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('approved', _('Onaylandı')),
        ('paid', _('Ödendi')),
        ('rejected', _('Reddedildi')),
    ]
    
    expense_category = models.CharField(_('Gider Kategorisi'), max_length=20, choices=EXPENSE_CATEGORY_CHOICES)
    description = models.TextField(_('Açıklama'))
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    expense_date = models.DateField(_('Gider Tarihi'))
    payment_due_date = models.DateField(_('Son Ödeme Tarihi'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='expenses', blank=True, null=True)
    payment_date = models.DateField(_('Ödeme Tarihi'), blank=True, null=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, related_name='expense', blank=True, null=True)
    receipt = models.FileField(_('Fiş/Fatura'), upload_to='expense_receipts/', blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_expenses')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='approved_expenses', blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Gider')
        verbose_name_plural = _('Giderler')
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.get_expense_category_display()} - {self.amount} TL - {self.expense_date}"
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def is_overdue(self):
        if not self.payment_due_date:
            return False
        return self.payment_due_date < timezone.now().date() and self.status not in ['paid', 'rejected']

class FinancialReport(models.Model):
    """Finansal rapor modeli"""
    
    REPORT_TYPE_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('monthly', _('Aylık')),
        ('quarterly', _('Üç Aylık')),
        ('yearly', _('Yıllık')),
        ('custom', _('Özel')),
    ]
    
    report_type = models.CharField(_('Rapor Tipi'), max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(_('Başlık'), max_length=255)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    total_income = models.DecimalField(_('Toplam Gelir'), max_digits=12, decimal_places=2)
    total_expense = models.DecimalField(_('Toplam Gider'), max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(_('Net Kar'), max_digits=12, decimal_places=2)
    report_data = models.JSONField(_('Rapor Verileri'), default=dict)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='generated_reports')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Finansal Rapor')
        verbose_name_plural = _('Finansal Raporlar')
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
    
    def save(self, *args, **kwargs):
        # Net karı hesapla
        self.net_profit = self.total_income - self.total_expense
        super().save(*args, **kwargs)
