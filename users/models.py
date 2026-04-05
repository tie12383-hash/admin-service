from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Телефон')
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name='Страна')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        permissions = [
            ('can_view_all_mailings', 'Может просматривать все рассылки'),
            ('can_view_all_clients', 'Может просматривать всех клиентов'),
            ('can_block_users', 'Может блокировать пользователей'),
            ('can_disable_mailings', 'Может отключать рассылки'),
        ]