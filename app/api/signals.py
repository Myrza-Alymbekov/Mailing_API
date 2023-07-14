from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


from .models import Mailing, Client, Message
from .tasks import send_mailing, schedule_mailing


@receiver(post_save, sender=Mailing)
def create_messages_for_clients(sender, instance, created, **kwargs):
    if created:
        current_time = timezone.now()
        clients = Client.objects.filter(operator_code=instance.operator_code, tag__in=instance.tag.all())
        for client in clients:
            Message.objects.create(creation_time=instance.start_time, mailing=instance, client=client)

        if instance.start_time <= current_time <= instance.end_time:
            # Вызываем функцию schedule_mailing с аргументом mailing_id
            schedule_mailing(instance.id)

        if instance.start_time > current_time:
            delay = (instance.start_time - current_time).total_seconds()
            # Используем apply_async для асинхронного выполнения schedule_mailing с указанием аргумента mailing_id и задержки
            schedule_mailing.apply_async(args=[instance.id], countdown=delay)
