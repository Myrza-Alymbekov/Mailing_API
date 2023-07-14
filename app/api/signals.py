from datetime import datetime
from django.utils import timezone

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Mailing, Client, Message
from .tasks import send_mailing, schedule_mailing


@receiver(post_save, sender=Mailing)
def create_messages_for_clients(sender, instance, created, **kwargs):
    if created:
        current_time = timezone.localtime(timezone.now())
        tags = instance.tag.all()

        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tag=tag)

        clients = Client.objects.filter(
            operator_code=instance.operator_code
        ).filter(q_objects).distinct()
        for client in clients:
            messages = Message.objects.filter(mailing=instance, client=client)
            if not messages.exists():
                Message.objects.create(
                    creation_time=instance.start_time,
                    mailing=instance,
                    client=client
                )

        if instance.start_time <= current_time <= instance.end_time:
            schedule_mailing(instance.id)

        if instance.start_time > current_time:
            delay = (instance.start_time - current_time).total_seconds()
            schedule_mailing.apply_async(args=[instance.id], countdown=delay)
