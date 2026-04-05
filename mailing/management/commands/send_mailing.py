from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from mailing.models import Mailing, Attempt
from config import settings

class Command(BaseCommand):
    help = 'Запускает все активные рассылки, время которых наступило'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        )
        for mailing in mailings:
            mailing.update_status()
            if mailing.status != 'started':
                continue
            for client in mailing.recipients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                    )
                    Attempt.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response='OK'
                    )
                except Exception as e:
                    Attempt.objects.create(
                        mailing=mailing,
                        status='failure',
                        server_response=str(e)
                    )
            self.stdout.write(self.style.SUCCESS(f'Рассылка {mailing.id} обработана'))
