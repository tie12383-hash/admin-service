from django.contrib import admin
from django.urls import path, include
from mailing.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),
    path('users/', include('users.urls')),
    path('mailing/', include('mailing.urls')),
]