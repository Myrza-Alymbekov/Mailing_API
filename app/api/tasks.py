import os
from datetime import datetime

import requests
from celery import shared_task
import pytz

from .models import Mailing, Message
from project.celery import app

token = os.environ.get('TOKEN')


@shared_task()
def schedule_mailing(mailing_id):
    messages = Message.objects.filter(mailing_id=mailing_id)

    for message in messages:
        client_timezone = pytz.timezone(message.client.timezone)

        # Преобразование времени начала рассылки во временную зону клиента
        client_start_time = datetime.now().astimezone(client_timezone)

        current_time = datetime.now(client_timezone)

        if client_start_time <= current_time:
            send_mailing(message_id=message.id)
        else:
            delay = (client_start_time - current_time).total_seconds()

            # Отправка сообщения в фоновом режиме с задержкой
            send_mailing.apply_async(message_id=message.id, countdown=delay)


@shared_task()
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
        message.send_status = 'Доставлено'
    else:
        message.send_status = 'Не отправлено'
    message.save()

