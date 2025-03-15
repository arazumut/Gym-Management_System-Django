from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Özel kullanıcı modeli için yönetici sınıfı"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Normal kullanıcı oluşturma"""
        if not email:
            raise ValueError(_('Email adresi gereklidir'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Süper kullanıcı oluşturma"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser is_staff=True olmalıdır.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser is_superuser=True olmalıdır.'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Özel kullanıcı modeli"""
    
    # Kullanıcı rolleri
    ADMIN = 'admin'
    MANAGER = 'manager'
    TRAINER = 'trainer'
    RECEPTIONIST = 'receptionist'
    MEMBER = 'member'
    
    ROLE_CHOICES = [
        (ADMIN, _('Yönetici')),
        (MANAGER, _('Müdür')),
        (TRAINER, _('Eğitmen')),
        (RECEPTIONIST, _('Resepsiyon')),
        (MEMBER, _('Üye')),
    ]
    
    email = models.EmailField(_('Email Adresi'), unique=True)
    first_name = models.CharField(_('Ad'), max_length=30, blank=True)
    last_name = models.CharField(_('Soyad'), max_length=30, blank=True)
    role = models.CharField(_('Rol'), max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    phone_number = models.CharField(_('Telefon numarası'), max_length=15, blank=True, null=True)
    address = models.TextField(_('Adres'), blank=True, null=True)
    profile_picture = models.ImageField(_('Profil fotoğrafı'), upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(_('Doğum tarihi'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    is_staff = models.BooleanField(_('Personel Durumu'), default=False)
    date_joined = models.DateTimeField(_('Kayıt Tarihi'), auto_now_add=True)
    last_login = models.DateTimeField(_('Son giriş'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    @property
    def is_manager(self):
        return self.role == self.MANAGER
    
    @property
    def is_trainer(self):
        return self.role == self.TRAINER
    
    @property
    def is_receptionist(self):
        return self.role == self.RECEPTIONIST
    
    @property
    def is_member(self):
        return self.role == self.MEMBER

    def get_username(self):
        return self.email

    @property
    def username(self):
        """Return the email as username."""
        return self.email
