from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.utils import timezone
from .models import Client, Message, Mailing, Attempt
from .forms import ClientForm, MessageForm, MailingForm
from config import settings

# Группы доступа
class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('mailing.can_view_all_mailings')

# Клиенты
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_clients'):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

# Аналогично MessageViewSet и MailingViewSet
# В MailingDetailView переопределён get_object для вызова update_status

class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

# Ручной запуск рассылки
def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.owner != request.user and not request.user.has_perm('mailing.can_disable_mailings'):
        return redirect('mailing:mailing_list')
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        return render(request, 'mailing/error.html', {'message': 'Рассылка не может быть запущена вне временного интервала.'})
    # Логика отправки
    for client in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Письмо успешно отправлено'
            )
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status='failure',
                server_response=str(e)
            )
    return redirect('mailing:mailing_detail', pk=pk)

# Главная страница со статистикой кешируется
def dashboard(request):
    cache_key = 'dashboard_stats'
    stats = cache.get(cache_key)
    if not stats:
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            status='started'
        ).count()
        unique_clients = Client.objects.count()
        stats = {
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'unique_clients': unique_clients,
        }
        cache.set(cache_key, stats, 60 * 5)
    return render(request, 'mailing/dashboard.html', {'stats': stats})
    if request.user.is_authenticated:
        user_mailings = Mailing.objects.filter(owner=request.user)
        user_attempts = Attempt.objects.filter(mailing__in=user_mailings)
        user_success = user_attempts.filter(status='success').count()
        user_failure = user_attempts.filter(status='failure').count()
        user_total_sent = user_attempts.count()
    else:
        user_success = user_failure = user_total_sent = 0

    return render(request, 'mailing/dashboard.html', {
        'stats': stats,
        'user_success': user_success,
        'user_failure': user_failure,
        'user_total_sent': user_total_sent,
    })

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        return Attempt.objects.filter(mailing__owner=self.request.user).order_by('-attempt_time')

# Страница статистики пользователя
def user_stats(request):
    user = request.user
    mailings = Mailing.objects.filter(owner=user)
    attempts = Attempt.objects.filter(mailing__in=mailings)
    success_count = attempts.filter(status='success').count()
    failure_count = attempts.filter(status='failure').count()
    total_sent = attempts.count()
    return render(request, 'mailing/user_stats.html', {
        'success_count': success_count,
        'failure_count': failure_count,
        'total_sent': total_sent,
        'mailings': mailings,
    })

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)