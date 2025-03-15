from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class ClassCategory(models.Model):
    """Ders kategorisi modeli"""
    
    name = models.CharField(_('Kategori Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    color = models.CharField(_('Renk Kodu'), max_length=7, help_text=_('Örn: #FF5733'), default='#3498db')
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ders Kategorisi')
        verbose_name_plural = _('Ders Kategorileri')
    
    def __str__(self):
        return self.name

class ClassRoom(models.Model):
    """Ders salonu modeli"""
    
    name = models.CharField(_('Salon Adı'), max_length=100)
    location = models.CharField(_('Konum'), max_length=100)
    capacity = models.PositiveIntegerField(_('Kapasite'))
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    equipment = models.TextField(_('Ekipmanlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ders Salonu')
        verbose_name_plural = _('Ders Salonları')
    
    def __str__(self):
        return f"{self.name} ({self.capacity} kişilik)"

class ClassTemplate(models.Model):
    """Ders şablonu modeli"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
        ('all_levels', _('Tüm Seviyeler')),
    ]
    
    name = models.CharField(_('Ders Adı'), max_length=100)
    category = models.ForeignKey(ClassCategory, on_delete=models.CASCADE, related_name='class_templates')
    description = models.TextField(_('Açıklama'))
    duration_minutes = models.PositiveIntegerField(_('Süre (dakika)'))
    difficulty = models.CharField(_('Zorluk Seviyesi'), max_length=20, choices=DIFFICULTY_CHOICES)
    benefits = models.TextField(_('Faydaları'), blank=True, null=True)
    requirements = models.TextField(_('Gereksinimler'), blank=True, null=True)
    image = models.ImageField(_('Görsel'), upload_to='class_templates/', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ders Şablonu')
        verbose_name_plural = _('Ders Şablonları')
    
    def __str__(self):
        return f"{self.name} - {self.get_difficulty_display()}"

class ClassSchedule(models.Model):
    """Ders programı modeli"""
    
    WEEKDAY_CHOICES = [
        (0, _('Pazartesi')),
        (1, _('Salı')),
        (2, _('Çarşamba')),
        (3, _('Perşembe')),
        (4, _('Cuma')),
        (5, _('Cumartesi')),
        (6, _('Pazar')),
    ]
    
    RECURRENCE_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('biweekly', _('İki Haftada Bir')),
        ('monthly', _('Aylık')),
        ('none', _('Tekrar Yok')),
    ]
    
    class_template = models.ForeignKey(ClassTemplate, on_delete=models.CASCADE, related_name='schedules')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_schedules')
    room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='class_schedules')
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'), blank=True, null=True)
    weekday = models.IntegerField(_('Haftanın Günü'), choices=WEEKDAY_CHOICES)
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    recurrence = models.CharField(_('Tekrar'), max_length=20, choices=RECURRENCE_CHOICES, default='weekly')
    max_participants = models.PositiveIntegerField(_('Maksimum Katılımcı Sayısı'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ders Programı')
        verbose_name_plural = _('Ders Programları')
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.class_template.name} - {self.get_weekday_display()} {self.start_time.strftime('%H:%M')}"
    
    @property
    def duration_minutes(self):
        start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
        end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds // 60
    
    @property
    def is_expired(self):
        if not self.end_date:
            return False
        return self.end_date < timezone.now().date()
    
    @property
    def current_participant_count(self):
        return self.class_sessions.filter(date=timezone.now().date()).first().participants.count() if self.class_sessions.filter(date=timezone.now().date()).exists() else 0
    
    @property
    def has_availability(self):
        return self.current_participant_count < self.max_participants

class ClassSession(models.Model):
    """Ders seansı modeli"""
    
    STATUS_CHOICES = [
        ('scheduled', _('Planlandı')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='class_sessions')
    date = models.DateField(_('Tarih'))
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_sessions')
    room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='class_sessions')
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ders Seansı')
        verbose_name_plural = _('Ders Seansları')
        ordering = ['date', 'start_time']
        unique_together = ('class_schedule', 'date')
    
    def __str__(self):
        return f"{self.class_schedule.class_template.name} - {self.date} {self.start_time.strftime('%H:%M')}"
    
    @property
    def duration_minutes(self):
        start_datetime = timezone.datetime.combine(self.date, self.start_time)
        end_datetime = timezone.datetime.combine(self.date, self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds // 60
    
    @property
    def is_past(self):
        now = timezone.now()
        session_datetime = timezone.datetime.combine(self.date, self.end_time)
        return session_datetime < now
    
    @property
    def participant_count(self):
        return self.participants.count()
    
    @property
    def has_availability(self):
        return self.participant_count < self.class_schedule.max_participants

class ClassParticipant(models.Model):
    """Ders katılımcısı modeli"""
    
    ATTENDANCE_CHOICES = [
        ('registered', _('Kayıtlı')),
        ('attended', _('Katıldı')),
        ('no_show', _('Gelmedi')),
        ('cancelled', _('İptal Etti')),
    ]
    
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='participants')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_participations')
    registration_time = models.DateTimeField(_('Kayıt Zamanı'), auto_now_add=True)
    attendance_status = models.CharField(_('Katılım Durumu'), max_length=20, choices=ATTENDANCE_CHOICES, default='registered')
    check_in_time = models.DateTimeField(_('Giriş Zamanı'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Ders Katılımcısı')
        verbose_name_plural = _('Ders Katılımcıları')
        unique_together = ('class_session', 'member')
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.class_session}"
    
    @property
    def is_checked_in(self):
        return self.check_in_time is not None

class ClassWaitingList(models.Model):
    """Ders bekleme listesi modeli"""
    
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='waiting_list')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_waiting_lists')
    registration_time = models.DateTimeField(_('Kayıt Zamanı'), auto_now_add=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    class Meta:
        verbose_name = _('Ders Bekleme Listesi')
        verbose_name_plural = _('Ders Bekleme Listeleri')
        ordering = ['registration_time']
        unique_together = ('class_session', 'member')
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.class_session}"
