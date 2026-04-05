from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'avatar', 'phone', 'country')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }