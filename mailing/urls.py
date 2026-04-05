from django.urls import path
from . import views

app_name = 'mailing'
urlpatterns = [
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('start/<int:pk>/', views.start_mailing, name='start_mailing'),
    path('stats/', views.user_stats, name='user_stats'),
]
