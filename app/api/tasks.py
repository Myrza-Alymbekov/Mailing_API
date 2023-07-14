import os
from datetime import datetime

import requests
from celery import shared_task
from pytz import timezone

from .models import Mailing, Message

token = os.environ.get('TOKEN')

@shared_task
def send_mailing(message_id):
    message = Message.objects.get(id=message_id)
    data = {
        "id": message.id,
        "phone": f'7{message.client.operator_code}{message.client.phone_number}',
        "text": message.mailing.text
    }
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.post('https://probe.fbrq.cloud/v1/send/1', json=data, headers=headers)

    # Проверяем код состояния ответа
    if response.status_code == 200:
        message.status = 'Доставлено'
    else:
        message.status = 'Не отправлено'
    message.save()


@shared_task
def schedule_mailing(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)
    messages = mailing.message_set.all()

    for message in messages:
        client_timezone = timezone(message.client.timezone)

        # Преобразование времени начала рассылки во временную зону клиента
        client_start_time = datetime.now().astimezone(client_timezone)

        current_time = datetime.now(client_timezone)

        if client_start_time <= current_time:
            send_mailing(message_id=message.id)
        else:
            delay = (client_start_time - current_time).total_seconds()
            send_mailing.apply_async(args=[message.id], countdown=delay)




# @receiver(pre_save, sender=Mailing)
# def update_message_status(sender, instance, **kwargs):
#     if instance.pk is None:  # Only for newly created messages
#         # Set the initial send_status as 'Не отправлено' (Not sent)
#         instance.send_status = 'Не отправлено'
