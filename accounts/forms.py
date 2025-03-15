from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm
from .models import User

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label=_('Ad'), required=False)
    last_name = forms.CharField(max_length=30, label=_('Soyad'), required=False)
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user 