from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
]