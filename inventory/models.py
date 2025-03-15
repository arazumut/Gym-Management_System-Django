from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class InventoryCategory(models.Model):
    """Envanter kategorisi modeli"""
    
    name = models.CharField(_('Kategori Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Envanter Kategorisi')
        verbose_name_plural = _('Envanter Kategorileri')
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Supplier(models.Model):
    """Tedarikçi modeli"""
    
    name = models.CharField(_('Tedarikçi Adı'), max_length=100)
    contact_person = models.CharField(_('İletişim Kişisi'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('E-posta'), blank=True, null=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True, null=True)
    address = models.TextField(_('Adres'), blank=True, null=True)
    website = models.URLField(_('Web Sitesi'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Tedarikçi')
        verbose_name_plural = _('Tedarikçiler')
    
    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    """Envanter öğesi modeli"""
    
    CONDITION_CHOICES = [
        ('new', _('Yeni')),
        ('good', _('İyi')),
        ('fair', _('Orta')),
        ('poor', _('Kötü')),
        ('broken', _('Bozuk')),
    ]
    
    name = models.CharField(_('Öğe Adı'), max_length=100)
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE, related_name='items')
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    sku = models.CharField(_('Stok Kodu (SKU)'), max_length=50, unique=True)
    barcode = models.CharField(_('Barkod'), max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('Miktar'))
    min_quantity = models.PositiveIntegerField(_('Minimum Miktar'), default=0)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, related_name='items', blank=True, null=True)
    condition = models.CharField(_('Durum'), max_length=20, choices=CONDITION_CHOICES, default='new')
    location = models.CharField(_('Konum'), max_length=100, blank=True, null=True)
    image = models.ImageField(_('Görsel'), upload_to='inventory_items/', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Envanter Öğesi')
        verbose_name_plural = _('Envanter Öğeleri')
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity
    
    @property
    def stock_value(self):
        if self.unit_price:
            return self.quantity * self.unit_price
        return None

class InventoryTransaction(models.Model):
    """Envanter işlemi modeli"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', _('Satın Alma')),
        ('sale', _('Satış')),
        ('return', _('İade')),
        ('adjustment', _('Düzeltme')),
        ('transfer', _('Transfer')),
        ('loss', _('Kayıp/Hasar')),
    ]
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(_('İşlem Tipi'), max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.IntegerField(_('Miktar'))
    transaction_date = models.DateTimeField(_('İşlem Tarihi'), default=timezone.now)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(_('Toplam Fiyat'), max_digits=10, decimal_places=2, blank=True, null=True)
    reference_number = models.CharField(_('Referans Numarası'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inventory_transactions')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Envanter İşlemi')
        verbose_name_plural = _('Envanter İşlemleri')
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} - {self.quantity} - {self.transaction_date.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Toplam fiyatı hesapla
        if self.unit_price and not self.total_price:
            self.total_price = self.quantity * self.unit_price
        
        # Stok miktarını güncelle
        is_new = self.pk is None
        if is_new:
            if self.transaction_type in ['purchase', 'return']:
                self.item.quantity += self.quantity
            elif self.transaction_type in ['sale', 'loss']:
                self.item.quantity -= self.quantity
            elif self.transaction_type == 'adjustment':
                # Düzeltme işlemi için miktar doğrudan değiştirilir
                pass
            self.item.save()
        
        super().save(*args, **kwargs)

class MaintenanceSchedule(models.Model):
    """Bakım programı modeli"""
    
    FREQUENCY_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('biweekly', _('İki Haftalık')),
        ('monthly', _('Aylık')),
        ('quarterly', _('Üç Aylık')),
        ('biannual', _('Altı Aylık')),
        ('annual', _('Yıllık')),
        ('custom', _('Özel')),
    ]
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='maintenance_schedules')
    title = models.CharField(_('Başlık'), max_length=100)
    description = models.TextField(_('Açıklama'))
    frequency = models.CharField(_('Sıklık'), max_length=20, choices=FREQUENCY_CHOICES)
    last_maintenance_date = models.DateField(_('Son Bakım Tarihi'), blank=True, null=True)
    next_maintenance_date = models.DateField(_('Sonraki Bakım Tarihi'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Bakım Programı')
        verbose_name_plural = _('Bakım Programları')
        ordering = ['next_maintenance_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.title} - {self.next_maintenance_date}"
    
    @property
    def is_overdue(self):
        return self.next_maintenance_date < timezone.now().date()
    
    @property
    def days_until_next_maintenance(self):
        return (self.next_maintenance_date - timezone.now().date()).days

class MaintenanceLog(models.Model):
    """Bakım kaydı modeli"""
    
    STATUS_CHOICES = [
        ('scheduled', _('Planlandı')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.CASCADE, related_name='logs', blank=True, null=True)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='maintenance_logs')
    title = models.CharField(_('Başlık'), max_length=100)
    description = models.TextField(_('Açıklama'))
    maintenance_date = models.DateField(_('Bakım Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    cost = models.DecimalField(_('Maliyet'), max_digits=10, decimal_places=2, blank=True, null=True)
    performed_by = models.CharField(_('Bakımı Yapan'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='maintenance_logs')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Bakım Kaydı')
        verbose_name_plural = _('Bakım Kayıtları')
        ordering = ['-maintenance_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.title} - {self.maintenance_date}"
    
    def save(self, *args, **kwargs):
        # Bakım tamamlandıysa, ilgili programın son ve sonraki bakım tarihlerini güncelle
        if self.status == 'completed' and self.schedule:
            self.schedule.last_maintenance_date = self.maintenance_date
            
            # Sonraki bakım tarihini hesapla
            if self.schedule.frequency == 'daily':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=1)
            elif self.schedule.frequency == 'weekly':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=7)
            elif self.schedule.frequency == 'biweekly':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=14)
            elif self.schedule.frequency == 'monthly':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=30)
            elif self.schedule.frequency == 'quarterly':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=90)
            elif self.schedule.frequency == 'biannual':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=180)
            elif self.schedule.frequency == 'annual':
                self.schedule.next_maintenance_date = self.maintenance_date + timezone.timedelta(days=365)
            
            self.schedule.save()
        
        super().save(*args, **kwargs)

class EquipmentAssignment(models.Model):
    """Ekipman zimmet modeli"""
    
    STATUS_CHOICES = [
        ('assigned', _('Zimmetlendi')),
        ('returned', _('İade Edildi')),
        ('lost', _('Kayıp')),
        ('damaged', _('Hasarlı')),
    ]
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_equipment')
    assigned_date = models.DateField(_('Zimmet Tarihi'))
    expected_return_date = models.DateField(_('Beklenen İade Tarihi'), blank=True, null=True)
    return_date = models.DateField(_('İade Tarihi'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='assigned')
    condition_on_assignment = models.CharField(_('Zimmet Anındaki Durum'), max_length=20, choices=InventoryItem.CONDITION_CHOICES)
    condition_on_return = models.CharField(_('İade Anındaki Durum'), max_length=20, choices=InventoryItem.CONDITION_CHOICES, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ekipman Zimmeti')
        verbose_name_plural = _('Ekipman Zimmetleri')
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.assigned_to.get_full_name()} - {self.assigned_date}"
    
    @property
    def is_overdue(self):
        if not self.expected_return_date or self.status != 'assigned':
            return False
        return self.expected_return_date < timezone.now().date() and not self.return_date
    
    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.expected_return_date).days
