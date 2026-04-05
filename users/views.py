from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .forms import UserRegistrationForm, UserProfileForm
from .models import User

class UserLoginView(LoginView):
    template_name = 'users/login.html'

class UserLogoutView(LogoutView):
    pass

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
