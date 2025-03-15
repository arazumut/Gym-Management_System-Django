from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class Announcement(models.Model):
    """Duyuru modeli"""
    
    PRIORITY_CHOICES = [
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('urgent', _('Acil')),
    ]
    
    title = models.CharField(_('Başlık'), max_length=200)
    content = models.TextField(_('İçerik'))
    priority = models.CharField(_('Öncelik'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(_('Başlangıç Tarihi'), default=timezone.now)
    end_date = models.DateField(_('Bitiş Tarihi'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Duyuru')
        verbose_name_plural = _('Duyurular')
        ordering = ['-priority', '-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.end_date:
            return self.end_date < timezone.now().date()
        return False

class DashboardWidget(models.Model):
    """Dashboard widget modeli"""
    
    WIDGET_TYPE_CHOICES = [
        ('members_count', _('Üye Sayısı')),
        ('active_memberships', _('Aktif Üyelikler')),
        ('revenue_chart', _('Gelir Grafiği')),
        ('expense_chart', _('Gider Grafiği')),
        ('attendance_chart', _('Katılım Grafiği')),
        ('class_popularity', _('Ders Popülerliği')),
        ('trainer_performance', _('Eğitmen Performansı')),
        ('equipment_usage', _('Ekipman Kullanımı')),
        ('upcoming_classes', _('Yaklaşan Dersler')),
        ('expiring_memberships', _('Sona Eren Üyelikler')),
        ('low_stock_items', _('Azalan Stok Ürünleri')),
        ('custom', _('Özel Widget')),
    ]
    
    name = models.CharField(_('Widget Adı'), max_length=100)
    widget_type = models.CharField(_('Widget Tipi'), max_length=50, choices=WIDGET_TYPE_CHOICES)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    config = models.JSONField(_('Konfigürasyon'), default=dict)
    position = models.PositiveSmallIntegerField(_('Pozisyon'), default=0)
    size = models.CharField(_('Boyut'), max_length=20, default='medium')
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgetları')
        ordering = ['position']
    
    def __str__(self):
        return self.name

class UserDashboard(models.Model):
    """Kullanıcı dashboard modeli"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboard')
    widgets = models.ManyToManyField(DashboardWidget, through='UserDashboardWidget')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Dashboard')
        verbose_name_plural = _('Kullanıcı Dashboardları')
    
    def __str__(self):
        return f"{self.user.get_full_name()} Dashboard"

class UserDashboardWidget(models.Model):
    """Kullanıcı dashboard widget ilişki modeli"""
    
    user_dashboard = models.ForeignKey(UserDashboard, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name='user_widgets')
    position = models.PositiveSmallIntegerField(_('Pozisyon'), default=0)
    is_visible = models.BooleanField(_('Görünür'), default=True)
    custom_config = models.JSONField(_('Özel Konfigürasyon'), default=dict, blank=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Dashboard Widget')
        verbose_name_plural = _('Kullanıcı Dashboard Widgetları')
        ordering = ['position']
        unique_together = ('user_dashboard', 'widget')
    
    def __str__(self):
        return f"{self.user_dashboard.user.get_full_name()} - {self.widget.name}"

class Report(models.Model):
    """Rapor modeli"""
    
    REPORT_TYPE_CHOICES = [
        ('membership', _('Üyelik Raporu')),
        ('financial', _('Finansal Rapor')),
        ('attendance', _('Katılım Raporu')),
        ('class', _('Ders Raporu')),
        ('trainer', _('Eğitmen Raporu')),
        ('inventory', _('Envanter Raporu')),
        ('staff', _('Personel Raporu')),
        ('custom', _('Özel Rapor')),
    ]
    
    PERIOD_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('monthly', _('Aylık')),
        ('quarterly', _('Üç Aylık')),
        ('yearly', _('Yıllık')),
        ('custom', _('Özel')),
    ]
    
    name = models.CharField(_('Rapor Adı'), max_length=100)
    report_type = models.CharField(_('Rapor Tipi'), max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    period = models.CharField(_('Dönem'), max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    parameters = models.JSONField(_('Parametreler'), default=dict, blank=True)
    result_data = models.JSONField(_('Sonuç Verileri'), default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Rapor')
        verbose_name_plural = _('Raporlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()}) - {self.start_date} - {self.end_date}"

class Notification(models.Model):
    """Bildirim modeli"""
    
    TYPE_CHOICES = [
        ('info', _('Bilgi')),
        ('success', _('Başarı')),
        ('warning', _('Uyarı')),
        ('error', _('Hata')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('Başlık'), max_length=100)
    message = models.TextField(_('Mesaj'))
    notification_type = models.CharField(_('Bildirim Tipi'), max_length=20, choices=TYPE_CHOICES, default='info')
    link = models.CharField(_('Bağlantı'), max_length=255, blank=True, null=True)
    is_read = models.BooleanField(_('Okundu'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Bildirim')
        verbose_name_plural = _('Bildirimler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"

class Task(models.Model):
    """Görev modeli"""
    
    PRIORITY_CHOICES = [
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('urgent', _('Acil')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    title = models.CharField(_('Başlık'), max_length=100)
    description = models.TextField(_('Açıklama'))
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(_('Öncelik'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(_('Son Tarih'), blank=True, null=True)
    completed_date = models.DateTimeField(_('Tamamlanma Tarihi'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Görev')
        verbose_name_plural = _('Görevler')
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < timezone.now()
        return False
