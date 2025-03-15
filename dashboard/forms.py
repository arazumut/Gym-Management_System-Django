from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Announcement, DashboardWidget, Report, Task

User = get_user_model()

class AnnouncementForm(forms.ModelForm):
    """Duyuru formu"""
    
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'start_date', 'end_date', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(_('Başlangıç tarihi bitiş tarihinden sonra olamaz.'))
        
        return cleaned_data

class DashboardWidgetForm(forms.ModelForm):
    """Dashboard widget formu"""
    
    class Meta:
        model = DashboardWidget
        fields = ['name', 'widget_type', 'description', 'config', 'position', 'size', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'config': forms.Textarea(attrs={'rows': 5, 'class': 'json-editor'}),
        }

class ReportForm(forms.ModelForm):
    """Rapor formu"""
    
    class Meta:
        model = Report
        fields = ['name', 'report_type', 'description', 'period', 'start_date', 'end_date', 'parameters']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'parameters': forms.Textarea(attrs={'rows': 5, 'class': 'json-editor'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(_('Başlangıç tarihi bitiş tarihinden sonra olamaz.'))
        
        return cleaned_data

class TaskForm(forms.ModelForm):
    """Görev formu"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'status', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece personel, eğitmen, resepsiyon ve yönetici rolündeki kullanıcıları göster
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True,
            role__in=['admin', 'manager', 'trainer', 'receptionist']
        )
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        
        if due_date and due_date < timezone.now():
            raise forms.ValidationError(_('Geçmiş tarihli görev oluşturamazsınız.'))
        
        return due_date

class NotificationFilterForm(forms.Form):
    """Bildirim filtreleme formu"""
    
    is_read = forms.ChoiceField(
        label=_('Okunma Durumu'),
        choices=[
            ('', _('Tümü')),
            ('true', _('Okunmuş')),
            ('false', _('Okunmamış')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TaskFilterForm(forms.Form):
    """Görev filtreleme formu"""
    
    status = forms.ChoiceField(
        label=_('Durum'),
        choices=[
            ('', _('Tümü')),
            ('pending', _('Beklemede')),
            ('in_progress', _('Devam Ediyor')),
            ('completed', _('Tamamlandı')),
            ('cancelled', _('İptal Edildi')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        label=_('Öncelik'),
        choices=[
            ('', _('Tümü')),
            ('low', _('Düşük')),
            ('medium', _('Orta')),
            ('high', _('Yüksek')),
            ('urgent', _('Acil')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        label=_('Arama'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Başlık veya açıklama ara...')})
    ) 