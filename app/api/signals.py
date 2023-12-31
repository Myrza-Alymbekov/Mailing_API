from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Mailing, Client, Message
from .tasks import schedule_mailing


@receiver(post_save, sender=Mailing)
def create_messages_for_clients(sender, instance, created, **kwargs):
    if created:
        current_time = timezone.now()

        clients = Client.objects.filter(operator_code=instance.operator_code)

        for client in clients:
            if client.tag == instance.tag:
                Message.objects.create(creation_time=instance.start_time, mailing=instance, client=client)

        if instance.start_time <= current_time <= instance.end_time:
            schedule_mailing.delay(instance.id)

        if instance.start_time > current_time:
            delay = (instance.start_time - current_time).total_seconds()
            schedule_mailing.apply_async(args=[instance.id], countdown=delay)

