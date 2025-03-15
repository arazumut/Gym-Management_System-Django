from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class Department(models.Model):
    """Departman modeli"""
    
    name = models.CharField(_('Departman Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='managed_departments', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Departman')
        verbose_name_plural = _('Departmanlar')
    
    def __str__(self):
        return self.name

class StaffProfile(models.Model):
    """Personel profil modeli"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', _('Tam Zamanlı')),
        ('part_time', _('Yarı Zamanlı')),
        ('contract', _('Sözleşmeli')),
        ('intern', _('Stajyer')),
        ('temporary', _('Geçici')),
    ]
    
    staff = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='staff', blank=True, null=True)
    position = models.CharField(_('Pozisyon'), max_length=100)
    employment_type = models.CharField(_('Çalışma Tipi'), max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    hire_date = models.DateField(_('İşe Başlama Tarihi'))
    end_date = models.DateField(_('İşten Ayrılma Tarihi'), blank=True, null=True)
    salary = models.DecimalField(_('Maaş'), max_digits=10, decimal_places=2)
    emergency_contact_name = models.CharField(_('Acil Durum Kişisi'), max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(_('Acil Durum Telefonu'), max_length=20, blank=True, null=True)
    bank_account = models.CharField(_('Banka Hesabı'), max_length=50, blank=True, null=True)
    tax_id = models.CharField(_('Vergi Numarası'), max_length=20, blank=True, null=True)
    social_security_number = models.CharField(_('SGK Numarası'), max_length=20, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Personel Profili')
        verbose_name_plural = _('Personel Profilleri')
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.position}"
    
    @property
    def employment_duration(self):
        end = self.end_date if self.end_date else timezone.now().date()
        return (end - self.hire_date).days

class Attendance(models.Model):
    """Personel devam takip modeli"""
    
    STATUS_CHOICES = [
        ('present', _('Mevcut')),
        ('absent', _('Yok')),
        ('late', _('Geç')),
        ('half_day', _('Yarım Gün')),
        ('leave', _('İzinli')),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(_('Tarih'))
    check_in = models.TimeField(_('Giriş Saati'), blank=True, null=True)
    check_out = models.TimeField(_('Çıkış Saati'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Devam Kaydı')
        verbose_name_plural = _('Devam Kayıtları')
        unique_together = ('staff', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} - {self.get_status_display()}"
    
    @property
    def duration(self):
        if self.check_in and self.check_out:
            check_in_datetime = timezone.datetime.combine(timezone.now().date(), self.check_in)
            check_out_datetime = timezone.datetime.combine(timezone.now().date(), self.check_out)
            return (check_out_datetime - check_in_datetime).seconds // 60
        return None

class Leave(models.Model):
    """Personel izin modeli"""
    
    LEAVE_TYPE_CHOICES = [
        ('annual', _('Yıllık İzin')),
        ('sick', _('Hastalık İzni')),
        ('maternity', _('Doğum İzni')),
        ('paternity', _('Babalık İzni')),
        ('marriage', _('Evlilik İzni')),
        ('bereavement', _('Ölüm İzni')),
        ('unpaid', _('Ücretsiz İzin')),
        ('other', _('Diğer')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('approved', _('Onaylandı')),
        ('rejected', _('Reddedildi')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(_('İzin Tipi'), max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    reason = models.TextField(_('Sebep'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='approved_leaves', blank=True, null=True)
    approved_date = models.DateTimeField(_('Onay Tarihi'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İzin')
        verbose_name_plural = _('İzinler')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} - {self.end_date})"
    
    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_approved(self):
        return self.status == 'approved'

class Shift(models.Model):
    """Vardiya modeli"""
    
    name = models.CharField(_('Vardiya Adı'), max_length=100)
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vardiya')
        verbose_name_plural = _('Vardiyalar')
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    @property
    def duration_hours(self):
        start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
        end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
        if end_datetime < start_datetime:  # Gece vardiyası
            end_datetime += timezone.timedelta(days=1)
        return (end_datetime - start_datetime).seconds / 3600

class ShiftAssignment(models.Model):
    """Vardiya atama modeli"""
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments')
    date = models.DateField(_('Tarih'))
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vardiya Ataması')
        verbose_name_plural = _('Vardiya Atamaları')
        unique_together = ('staff', 'date')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.shift.name} - {self.date}"

class Performance(models.Model):
    """Personel performans değerlendirme modeli"""
    
    RATING_CHOICES = [
        (1, _('Çok Kötü')),
        (2, _('Kötü')),
        (3, _('Orta')),
        (4, _('İyi')),
        (5, _('Çok İyi')),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviewed_performances')
    review_date = models.DateField(_('Değerlendirme Tarihi'))
    period_start = models.DateField(_('Dönem Başlangıcı'))
    period_end = models.DateField(_('Dönem Sonu'))
    punctuality_rating = models.PositiveSmallIntegerField(_('Dakiklik Puanı'), choices=RATING_CHOICES)
    attendance_rating = models.PositiveSmallIntegerField(_('Devam Puanı'), choices=RATING_CHOICES)
    productivity_rating = models.PositiveSmallIntegerField(_('Verimlilik Puanı'), choices=RATING_CHOICES)
    quality_rating = models.PositiveSmallIntegerField(_('Kalite Puanı'), choices=RATING_CHOICES)
    teamwork_rating = models.PositiveSmallIntegerField(_('Takım Çalışması Puanı'), choices=RATING_CHOICES)
    communication_rating = models.PositiveSmallIntegerField(_('İletişim Puanı'), choices=RATING_CHOICES)
    overall_rating = models.PositiveSmallIntegerField(_('Genel Puan'), choices=RATING_CHOICES)
    strengths = models.TextField(_('Güçlü Yönler'), blank=True, null=True)
    areas_for_improvement = models.TextField(_('Geliştirilmesi Gereken Alanlar'), blank=True, null=True)
    goals = models.TextField(_('Hedefler'), blank=True, null=True)
    comments = models.TextField(_('Yorumlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Performans Değerlendirmesi')
        verbose_name_plural = _('Performans Değerlendirmeleri')
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.review_date} - {self.overall_rating}/5"
    
    @property
    def average_rating(self):
        ratings = [
            self.punctuality_rating,
            self.attendance_rating,
            self.productivity_rating,
            self.quality_rating,
            self.teamwork_rating,
            self.communication_rating
        ]
        return sum(ratings) / len(ratings)

class Payroll(models.Model):
    """Maaş bordrosu modeli"""
    
    STATUS_CHOICES = [
        ('draft', _('Taslak')),
        ('approved', _('Onaylandı')),
        ('paid', _('Ödendi')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payrolls')
    period_start = models.DateField(_('Dönem Başlangıcı'))
    period_end = models.DateField(_('Dönem Sonu'))
    basic_salary = models.DecimalField(_('Temel Maaş'), max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(_('Fazla Mesai Saati'), max_digits=6, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(_('Fazla Mesai Ücreti (Saatlik)'), max_digits=6, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(_('Fazla Mesai Tutarı'), max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(_('Prim'), max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(_('Ödenekler'), max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(_('Kesintiler'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('Vergi'), max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(_('Net Maaş'), max_digits=10, decimal_places=2)
    payment_date = models.DateField(_('Ödeme Tarihi'), blank=True, null=True)
    payment_method = models.CharField(_('Ödeme Yöntemi'), max_length=50, blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_payrolls')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='approved_payrolls', blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Maaş Bordrosu')
        verbose_name_plural = _('Maaş Bordroları')
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.period_start} - {self.period_end}"
    
    def save(self, *args, **kwargs):
        # Fazla mesai tutarını hesapla
        self.overtime_amount = self.overtime_hours * self.overtime_rate
        
        # Net maaşı hesapla
        self.net_salary = (
            self.basic_salary +
            self.overtime_amount +
            self.bonus +
            self.allowances -
            self.deductions -
            self.tax
        )
        
        super().save(*args, **kwargs)
