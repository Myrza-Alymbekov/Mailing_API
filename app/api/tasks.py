import os
from datetime import datetime

import requests
from celery import shared_task
from pytz import timezone

from .models import Mailing, Message
from project.celery import app

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjA2MDc1NTEsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Imh0dHBzOi8vdC5tZS9hdXJhcml6ZWQifQ.A1mo_ukujEUhQnCwR6eFWpgUuyQIXe_RAvarnIGhkEA'


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
        print(response.json())
    else:
        message.send_status = 'Не отправлено'
        print('error')
    message.save()


# @app.task
def schedule_mailing(mailing_id):
    messages = Message.objects.filter(mailing_id=mailing_id)

    for message in messages:
        # client_timezone = timezone(message.client.timezone)
        #
        # # Преобразование времени начала рассылки во временную зону клиента
        # client_start_time = datetime.now().astimezone(client_timezone)
        #
        # current_time = datetime.now(client_timezone)
        #
        # if client_start_time <= current_time:
        #     send_mailing(message_id=message.id)
        # else:
        #     delay = (client_start_time - current_time).total_seconds()
        #     send_mailing.apply_async(args=[message.id], countdown=delay)
        send_mailing(message_id=message.id)
