from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Mailing, Client, Message
from .tasks import send_mailing, schedule_mailing


@receiver(post_save, sender=Mailing)
def create_messages_for_clients(sender, instance, created, **kwargs):
    if created:
        current_time = datetime.now()
        clients = Client.objects.filter(operator_code=instance.operator_code, tag__in=instance.tag.all())
        for client in clients:
            Message.objects.create(creation_time=instance.start_time, mailing=instance, client=client)
        if instance.start_time <= current_time <= instance.end_time:
            schedule_mailing(mailing_id=instance.id)
        if instance.start_time > current_time:
            delay = (instance.start_time - current_time).total_seconds()
            schedule_mailing.apply_async(args=[instance.id], countdown=delay)
