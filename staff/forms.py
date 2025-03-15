from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Department, StaffProfile, Attendance, Leave, Shift, ShiftAssignment, Performance, Payroll

class DepartmentForm(forms.ModelForm):
    """Departman formu"""
    
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class StaffProfileForm(forms.ModelForm):
    """Personel profil formu"""
    
    class Meta:
        model = StaffProfile
        fields = [
            'department', 'position', 'employment_type', 'hire_date', 'end_date',
            'salary', 'emergency_contact_name', 'emergency_contact_phone',
            'bank_account', 'tax_id', 'social_security_number', 'notes'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AttendanceForm(forms.ModelForm):
    """Devam kaydı formu"""
    
    class Meta:
        model = Attendance
        fields = ['date', 'check_in', 'check_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class LeaveRequestForm(forms.ModelForm):
    """İzin talebi formu"""
    
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(_('Başlangıç tarihi bitiş tarihinden sonra olamaz.'))
            
            if start_date < timezone.now().date():
                raise forms.ValidationError(_('Geçmiş tarihli izin talebi oluşturamazsınız.'))
        
        return cleaned_data

class ShiftForm(forms.ModelForm):
    """Vardiya formu"""
    
    class Meta:
        model = Shift
        fields = ['name', 'start_time', 'end_time', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ShiftAssignmentForm(forms.ModelForm):
    """Vardiya atama formu"""
    
    class Meta:
        model = ShiftAssignment
        fields = ['staff', 'shift', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        staff = cleaned_data.get('staff')
        date = cleaned_data.get('date')
        
        if staff and date:
            # Aynı gün için başka bir vardiya ataması var mı kontrol et
            if ShiftAssignment.objects.filter(staff=staff, date=date).exists():
                raise forms.ValidationError(_('Bu personel için seçilen tarihte zaten bir vardiya ataması bulunmaktadır.'))
        
        return cleaned_data

class PerformanceForm(forms.ModelForm):
    """Performans değerlendirme formu"""
    
    class Meta:
        model = Performance
        fields = [
            'staff', 'reviewer', 'review_date', 'period_start', 'period_end',
            'punctuality_rating', 'attendance_rating', 'productivity_rating',
            'quality_rating', 'teamwork_rating', 'communication_rating',
            'overall_rating', 'strengths', 'areas_for_improvement', 'goals', 'comments'
        ]
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 3}),
            'goals': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end:
            if period_start > period_end:
                raise forms.ValidationError(_('Dönem başlangıç tarihi dönem bitiş tarihinden sonra olamaz.'))
        
        return cleaned_data

class PayrollForm(forms.ModelForm):
    """Maaş bordrosu formu"""
    
    class Meta:
        model = Payroll
        fields = [
            'staff', 'period_start', 'period_end', 'basic_salary',
            'overtime_hours', 'overtime_rate', 'bonus', 'allowances',
            'deductions', 'tax', 'payment_date', 'payment_method',
            'status', 'notes'
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end:
            if period_start > period_end:
                raise forms.ValidationError(_('Dönem başlangıç tarihi dönem bitiş tarihinden sonra olamaz.'))
        
        return cleaned_data 