from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class TrainerProfile(models.Model):
    """Eğitmen profil modeli"""
    
    SPECIALIZATION_CHOICES = [
        ('fitness', _('Fitness')),
        ('yoga', _('Yoga')),
        ('pilates', _('Pilates')),
        ('cardio', _('Kardiyo')),
        ('strength', _('Güç Antrenmanı')),
        ('crossfit', _('CrossFit')),
        ('boxing', _('Boks')),
        ('swimming', _('Yüzme')),
        ('nutrition', _('Beslenme')),
        ('other', _('Diğer')),
    ]
    
    trainer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_profile')
    specialization = models.CharField(_('Uzmanlık Alanı'), max_length=20, choices=SPECIALIZATION_CHOICES)
    secondary_specialization = models.CharField(_('İkincil Uzmanlık Alanı'), max_length=20, choices=SPECIALIZATION_CHOICES, blank=True, null=True)
    experience_years = models.PositiveIntegerField(_('Deneyim (Yıl)'))
    bio = models.TextField(_('Biyografi'))
    certifications = models.TextField(_('Sertifikalar'), blank=True, null=True)
    hourly_rate = models.DecimalField(_('Saatlik Ücret'), max_digits=10, decimal_places=2)
    available_hours = models.JSONField(_('Müsait Saatler'), default=dict, help_text=_('Eğitmenin müsait olduğu saatler'))
    max_clients = models.PositiveIntegerField(_('Maksimum Danışan Sayısı'), default=10)
    is_available = models.BooleanField(_('Müsait'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Eğitmen Profili')
        verbose_name_plural = _('Eğitmen Profilleri')
    
    def __str__(self):
        return f"{self.trainer.get_full_name()} - {self.get_specialization_display()}"
    
    @property
    def current_client_count(self):
        return self.clients.filter(is_active=True).count()
    
    @property
    def has_availability(self):
        return self.current_client_count < self.max_clients

class TrainerClient(models.Model):
    """Eğitmen-Danışan ilişki modeli"""
    
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_clients')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_trainers')
    start_date = models.DateField(_('Başlangıç tarihi'))
    end_date = models.DateField(_('Bitiş tarihi'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Eğitmen Danışanı')
        verbose_name_plural = _('Eğitmen Danışanları')
        unique_together = ('trainer', 'client')
    
    def __str__(self):
        return f"{self.trainer.get_full_name()} - {self.client.get_full_name()}"
    
    @property
    def is_expired(self):
        if not self.end_date:
            return False
        return self.end_date < timezone.now().date()

class TrainingProgram(models.Model):
    """Antrenman programı modeli"""
    
    PROGRAM_TYPE_CHOICES = [
        ('strength', _('Güç')),
        ('cardio', _('Kardiyo')),
        ('flexibility', _('Esneklik')),
        ('weight_loss', _('Kilo Verme')),
        ('muscle_gain', _('Kas Kazanımı')),
        ('endurance', _('Dayanıklılık')),
        ('rehabilitation', _('Rehabilitasyon')),
        ('general', _('Genel Fitness')),
        ('custom', _('Özel Program')),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
        ('expert', _('Uzman')),
    ]
    
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_training_programs')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_training_programs')
    title = models.CharField(_('Program Başlığı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    program_type = models.CharField(_('Program Tipi'), max_length=20, choices=PROGRAM_TYPE_CHOICES)
    difficulty = models.CharField(_('Zorluk Seviyesi'), max_length=20, choices=DIFFICULTY_CHOICES)
    start_date = models.DateField(_('Başlangıç tarihi'))
    end_date = models.DateField(_('Bitiş tarihi'))
    days_per_week = models.PositiveIntegerField(_('Haftalık Gün Sayısı'))
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Antrenman Programı')
        verbose_name_plural = _('Antrenman Programları')
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.title}"
    
    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()
    
    @property
    def days_left(self):
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now().date()).days

class TrainingSession(models.Model):
    """Antrenman seansı modeli"""
    
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='sessions')
    day_of_week = models.PositiveIntegerField(_('Haftanın Günü'), choices=[(1, _('Pazartesi')), (2, _('Salı')), (3, _('Çarşamba')), (4, _('Perşembe')), (5, _('Cuma')), (6, _('Cumartesi')), (7, _('Pazar'))])
    title = models.CharField(_('Seans Başlığı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    duration_minutes = models.PositiveIntegerField(_('Süre (dakika)'))
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Antrenman Seansı')
        verbose_name_plural = _('Antrenman Seansları')
        ordering = ['day_of_week']
    
    def __str__(self):
        return f"{self.program.title} - {self.get_day_of_week_display()} - {self.title}"

class Exercise(models.Model):
    """Egzersiz modeli"""
    
    MUSCLE_GROUP_CHOICES = [
        ('chest', _('Göğüs')),
        ('back', _('Sırt')),
        ('shoulders', _('Omuzlar')),
        ('arms', _('Kollar')),
        ('legs', _('Bacaklar')),
        ('core', _('Karın')),
        ('full_body', _('Tüm Vücut')),
        ('cardio', _('Kardiyo')),
        ('other', _('Diğer')),
    ]
    
    name = models.CharField(_('Egzersiz Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    muscle_group = models.CharField(_('Kas Grubu'), max_length=20, choices=MUSCLE_GROUP_CHOICES)
    instructions = models.TextField(_('Talimatlar'))
    video_url = models.URLField(_('Video URL'), blank=True, null=True)
    image = models.ImageField(_('Görsel'), upload_to='exercises/', blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Egzersiz')
        verbose_name_plural = _('Egzersizler')
    
    def __str__(self):
        return f"{self.name} - {self.get_muscle_group_display()}"

class SessionExercise(models.Model):
    """Seans egzersiz modeli"""
    
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='session_exercises')
    order = models.PositiveIntegerField(_('Sıra'))
    sets = models.PositiveIntegerField(_('Set Sayısı'))
    reps = models.CharField(_('Tekrar Sayısı'), max_length=50)
    rest_seconds = models.PositiveIntegerField(_('Dinlenme (saniye)'))
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Seans Egzersizi')
        verbose_name_plural = _('Seans Egzersizleri')
        ordering = ['order']
        unique_together = ('session', 'order')
    
    def __str__(self):
        return f"{self.session.title} - {self.exercise.name} - Set: {self.sets} Tekrar: {self.reps}"

class NutritionPlan(models.Model):
    """Beslenme planı modeli"""
    
    GOAL_CHOICES = [
        ('weight_loss', _('Kilo Verme')),
        ('muscle_gain', _('Kas Kazanımı')),
        ('maintenance', _('Kilo Koruma')),
        ('health', _('Genel Sağlık')),
        ('performance', _('Performans')),
        ('custom', _('Özel')),
    ]
    
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_nutrition_plans')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_nutrition_plans')
    title = models.CharField(_('Plan Başlığı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    goal = models.CharField(_('Hedef'), max_length=20, choices=GOAL_CHOICES)
    start_date = models.DateField(_('Başlangıç tarihi'))
    end_date = models.DateField(_('Bitiş tarihi'))
    daily_calories = models.PositiveIntegerField(_('Günlük Kalori'), blank=True, null=True)
    protein_grams = models.PositiveIntegerField(_('Protein (g)'), blank=True, null=True)
    carbs_grams = models.PositiveIntegerField(_('Karbonhidrat (g)'), blank=True, null=True)
    fat_grams = models.PositiveIntegerField(_('Yağ (g)'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Beslenme Planı')
        verbose_name_plural = _('Beslenme Planları')
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.title}"
    
    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()
    
    @property
    def days_left(self):
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now().date()).days

class Meal(models.Model):
    """Öğün modeli"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', _('Kahvaltı')),
        ('lunch', _('Öğle Yemeği')),
        ('dinner', _('Akşam Yemeği')),
        ('snack', _('Ara Öğün')),
        ('pre_workout', _('Antrenman Öncesi')),
        ('post_workout', _('Antrenman Sonrası')),
        ('other', _('Diğer')),
    ]
    
    nutrition_plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(_('Öğün Tipi'), max_length=20, choices=MEAL_TYPE_CHOICES)
    title = models.CharField(_('Başlık'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    time = models.TimeField(_('Saat'))
    calories = models.PositiveIntegerField(_('Kalori'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Öğün')
        verbose_name_plural = _('Öğünler')
        ordering = ['time']
    
    def __str__(self):
        return f"{self.nutrition_plan.title} - {self.get_meal_type_display()} - {self.title}"

class MealFood(models.Model):
    """Öğün yiyecek modeli"""
    
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(_('Yiyecek Adı'), max_length=100)
    quantity = models.CharField(_('Miktar'), max_length=50)
    calories = models.PositiveIntegerField(_('Kalori'), blank=True, null=True)
    protein = models.DecimalField(_('Protein (g)'), max_digits=6, decimal_places=2, blank=True, null=True)
    carbs = models.DecimalField(_('Karbonhidrat (g)'), max_digits=6, decimal_places=2, blank=True, null=True)
    fat = models.DecimalField(_('Yağ (g)'), max_digits=6, decimal_places=2, blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Öğün Yiyeceği')
        verbose_name_plural = _('Öğün Yiyecekleri')
    
    def __str__(self):
        return f"{self.meal.title} - {self.name} ({self.quantity})"

class TrainerAppointment(models.Model):
    """Eğitmen randevu modeli"""
    
    STATUS_CHOICES = [
        ('scheduled', _('Planlandı')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
        ('no_show', _('Gelmedi')),
    ]
    
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_appointments')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    date = models.DateField(_('Tarih'))
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Eğitmen Randevusu')
        verbose_name_plural = _('Eğitmen Randevuları')
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.trainer.get_full_name()} - {self.client.get_full_name()} - {self.date} {self.start_time}"
    
    @property
    def duration_minutes(self):
        start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
        end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
        duration = end_datetime - start_datetime
        return duration.seconds // 60
    
    @property
    def is_past(self):
        now = timezone.now()
        appointment_datetime = timezone.datetime.combine(self.date, self.end_time)
        return appointment_datetime < now
