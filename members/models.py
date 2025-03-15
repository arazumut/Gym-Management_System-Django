from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import datetime

class MembershipPlan(models.Model):
    """Üyelik paketleri modeli"""
    
    name = models.CharField(_('Paket adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    duration_days = models.PositiveIntegerField(_('Süre (gün)'))
    price = models.DecimalField(_('Fiyat'), max_digits=10, decimal_places=2)
    features = models.TextField(_('Özellikler'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Üyelik Planı')
        verbose_name_plural = _('Üyelik Planları')
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    """Üyelik modeli"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('paid', _('Ödendi')),
        ('overdue', _('Gecikmiş')),
        ('cancelled', _('İptal edildi')),
    ]
    
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='memberships')
    start_date = models.DateField(_('Başlangıç tarihi'))
    end_date = models.DateField(_('Bitiş tarihi'))
    payment_status = models.CharField(_('Ödeme durumu'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(_('Ödeme tarihi'), blank=True, null=True)
    amount_paid = models.DecimalField(_('Ödenen tutar'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Üyelik')
        verbose_name_plural = _('Üyelikler')
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.plan.name}"
    
    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()
    
    @property
    def days_left(self):
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now().date()).days
    
    @property
    def days_since_start(self):
        return (timezone.now().date() - self.start_date).days

class MemberMeasurement(models.Model):
    """Üye ölçüm takibi modeli"""
    
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='measurements')
    date = models.DateField(_('Ölçüm tarihi'))
    weight = models.DecimalField(_('Kilo (kg)'), max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(_('Boy (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_percentage = models.DecimalField(_('Vücut yağ oranı (%)'), max_digits=5, decimal_places=2, blank=True, null=True)
    muscle_mass = models.DecimalField(_('Kas kütlesi (kg)'), max_digits=5, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(_('Vücut kitle indeksi (BMI)'), max_digits=5, decimal_places=2, blank=True, null=True)
    chest = models.DecimalField(_('Göğüs (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    waist = models.DecimalField(_('Bel (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    hips = models.DecimalField(_('Kalça (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    arms = models.DecimalField(_('Kol (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    thighs = models.DecimalField(_('Bacak (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Üye Ölçümü')
        verbose_name_plural = _('Üye Ölçümleri')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.date}"
    
    def calculate_bmi(self):
        if self.weight and self.height:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return None
    
    def save(self, *args, **kwargs):
        if self.weight and self.height and not self.bmi:
            self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

class CheckInOut(models.Model):
    """Üye giriş-çıkış takibi modeli"""
    
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='check_ins')
    check_in_time = models.DateTimeField(_('Giriş zamanı'), auto_now_add=True)
    check_out_time = models.DateTimeField(_('Çıkış zamanı'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Giriş-Çıkış Kaydı')
        verbose_name_plural = _('Giriş-Çıkış Kayıtları')
        ordering = ['-check_in_time']
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.check_in_time.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duration(self):
        if self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None
    
    @property
    def is_checked_out(self):
        return self.check_out_time is not None
