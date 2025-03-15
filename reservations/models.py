from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class ReservableArea(models.Model):
    """Rezerve edilebilir alan modeli"""
    
    AREA_TYPE_CHOICES = [
        ('court', _('Kort')),
        ('pool', _('Havuz')),
        ('sauna', _('Sauna')),
        ('massage', _('Masaj Odası')),
        ('meeting', _('Toplantı Odası')),
        ('other', _('Diğer')),
    ]
    
    name = models.CharField(_('Alan Adı'), max_length=100)
    area_type = models.CharField(_('Alan Tipi'), max_length=20, choices=AREA_TYPE_CHOICES)
    location = models.CharField(_('Konum'), max_length=100)
    capacity = models.PositiveIntegerField(_('Kapasite'))
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    price_per_hour = models.DecimalField(_('Saatlik Ücret'), max_digits=10, decimal_places=2)
    image = models.ImageField(_('Görsel'), upload_to='reservable_areas/', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Rezerve Edilebilir Alan')
        verbose_name_plural = _('Rezerve Edilebilir Alanlar')
    
    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()})"

class AreaAvailability(models.Model):
    """Alan müsaitlik modeli"""
    
    WEEKDAY_CHOICES = [
        (0, _('Pazartesi')),
        (1, _('Salı')),
        (2, _('Çarşamba')),
        (3, _('Perşembe')),
        (4, _('Cuma')),
        (5, _('Cumartesi')),
        (6, _('Pazar')),
    ]
    
    area = models.ForeignKey(ReservableArea, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(_('Haftanın Günü'), choices=WEEKDAY_CHOICES)
    start_time = models.TimeField(_('Açılış Saati'))
    end_time = models.TimeField(_('Kapanış Saati'))
    is_available = models.BooleanField(_('Müsait'), default=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Alan Müsaitliği')
        verbose_name_plural = _('Alan Müsaitlikleri')
        ordering = ['weekday', 'start_time']
        unique_together = ('area', 'weekday')
    
    def __str__(self):
        return f"{self.area.name} - {self.get_weekday_display()} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

class AreaReservation(models.Model):
    """Alan rezervasyonu modeli"""
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('confirmed', _('Onaylandı')),
        ('cancelled', _('İptal Edildi')),
        ('completed', _('Tamamlandı')),
        ('no_show', _('Gelmedi')),
    ]
    
    area = models.ForeignKey(ReservableArea, on_delete=models.CASCADE, related_name='reservations')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='area_reservations')
    date = models.DateField(_('Tarih'))
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    number_of_people = models.PositiveIntegerField(_('Kişi Sayısı'), default=1)
    price = models.DecimalField(_('Fiyat'), max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(_('Ödendi'), default=False)
    payment_date = models.DateTimeField(_('Ödeme Tarihi'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Alan Rezervasyonu')
        verbose_name_plural = _('Alan Rezervasyonları')
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.area.name} - {self.member.get_full_name()} - {self.date} {self.start_time.strftime('%H:%M')}"
    
    @property
    def duration_hours(self):
        start_datetime = timezone.datetime.combine(self.date, self.start_time)
        end_datetime = timezone.datetime.combine(self.date, self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds / 3600
    
    @property
    def is_past(self):
        now = timezone.now()
        reservation_datetime = timezone.datetime.combine(self.date, self.end_time)
        return reservation_datetime < now
    
    def save(self, *args, **kwargs):
        if not self.price:
            # Fiyatı otomatik hesapla
            hours = self.duration_hours
            self.price = self.area.price_per_hour * hours
        super().save(*args, **kwargs)

class EquipmentCategory(models.Model):
    """Ekipman kategorisi modeli"""
    
    name = models.CharField(_('Kategori Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ekipman Kategorisi')
        verbose_name_plural = _('Ekipman Kategorileri')
    
    def __str__(self):
        return self.name

class Equipment(models.Model):
    """Ekipman modeli"""
    
    name = models.CharField(_('Ekipman Adı'), max_length=100)
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='equipments')
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    quantity = models.PositiveIntegerField(_('Toplam Adet'))
    available_quantity = models.PositiveIntegerField(_('Müsait Adet'))
    price_per_hour = models.DecimalField(_('Saatlik Ücret'), max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(_('Görsel'), upload_to='equipments/', blank=True, null=True)
    is_reservable = models.BooleanField(_('Rezerve Edilebilir'), default=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ekipman')
        verbose_name_plural = _('Ekipmanlar')
    
    def __str__(self):
        return f"{self.name} ({self.available_quantity}/{self.quantity})"
    
    @property
    def is_available(self):
        return self.available_quantity > 0

class EquipmentReservation(models.Model):
    """Ekipman rezervasyonu modeli"""
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('confirmed', _('Onaylandı')),
        ('cancelled', _('İptal Edildi')),
        ('checked_out', _('Teslim Alındı')),
        ('returned', _('İade Edildi')),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='reservations')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_reservations')
    quantity = models.PositiveIntegerField(_('Adet'), default=1)
    date = models.DateField(_('Tarih'))
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(_('Fiyat'), max_digits=10, decimal_places=2, blank=True, null=True)
    is_paid = models.BooleanField(_('Ödendi'), default=False)
    payment_date = models.DateTimeField(_('Ödeme Tarihi'), blank=True, null=True)
    checkout_time = models.DateTimeField(_('Teslim Alma Zamanı'), blank=True, null=True)
    return_time = models.DateTimeField(_('İade Zamanı'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ekipman Rezervasyonu')
        verbose_name_plural = _('Ekipman Rezervasyonları')
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.equipment.name} ({self.quantity}) - {self.member.get_full_name()} - {self.date} {self.start_time.strftime('%H:%M')}"
    
    @property
    def duration_hours(self):
        start_datetime = timezone.datetime.combine(self.date, self.start_time)
        end_datetime = timezone.datetime.combine(self.date, self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds / 3600
    
    @property
    def is_past(self):
        now = timezone.now()
        reservation_datetime = timezone.datetime.combine(self.date, self.end_time)
        return reservation_datetime < now
    
    def save(self, *args, **kwargs):
        if not self.price and self.equipment.price_per_hour:
            # Fiyatı otomatik hesapla
            hours = self.duration_hours
            self.price = self.equipment.price_per_hour * hours * self.quantity
        super().save(*args, **kwargs)
