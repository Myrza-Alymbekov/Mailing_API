import os
import pytz
import requests

from datetime import datetime

from celery import shared_task

from .models import Message


token = os.environ.get('TOKEN')


@shared_task()
def schedule_mailing(mailing_id):
    messages = Message.objects.filter(mailing_id=mailing_id)

    for message in messages:
        client_timezone = pytz.timezone(message.client.timezone)
        local_timezone = pytz.timezone('Europe/Moscow')

        client_start_time = pytz.utc.localize(datetime.utcnow()).astimezone(client_timezone)
        current_time = pytz.utc.localize(datetime.utcnow()).astimezone(local_timezone)

        if client_start_time < current_time:
            delay = (current_time.utcoffset() - client_start_time.utcoffset()).total_seconds()
            # Отправка сообщения в фоновом режиме с задержкой
            send_mailing.apply_async(args=[message.id], countdown=delay)
        else:
            send_mailing(message_id=message.id)


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

