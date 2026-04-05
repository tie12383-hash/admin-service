from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Создаёт группу менеджеров и назначает права'

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name='Менеджеры')

        permissions_codenames = [
            'can_view_all_mailings',
            'can_view_all_clients',
            'can_block_users',
            'can_disable_mailings'
        ]

        for codename in permissions_codenames:
            perm = Permission.objects.filter(codename=codename).first()
            if perm:
                managers_group.permissions.add(perm)
                self.stdout.write(f'Добавлено право: {codename}')
            else:
                self.stdout.write(self.style.WARNING(f'Право {codename} не найдено'))

        self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана/обновлена'))
