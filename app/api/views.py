import requests
from django.db.models import Count

from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Mailing, Client, Message, Tag
from .serializers import MailingSerializer, ClientSerializer, MessageSerializer, TagSerializer


class MailingPagePagination(PageNumberPagination):
    page_size = 10


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.annotate(num_messages=Count('message'))
    serializer_class = MailingSerializer
    pagination_class = MailingPagePagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class MailingStatisticsAPIView(APIView):

    @staticmethod
    def get(request):
        mailing_count = Mailing.objects.count()

        sent_messages_count = Message.objects.filter(send_status='Доставлено').count()
        in_progress_messages_count = Message.objects.filter(send_status='В процессе').count()
        not_sent_messages_count = Message.objects.filter(send_status='Не отправлено').count()

        statistics = {
            'mailing_count': mailing_count,
            'sent_messages_count': sent_messages_count,
            'in_progress_messages_count': in_progress_messages_count,
            'not_sent_messages_count': not_sent_messages_count,
        }

        return Response(statistics)


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjA2MDc1NTEsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Imh0dHBzOi8vdC5tZS9hdXJhcml6ZWQifQ.A1mo_ukujEUhQnCwR6eFWpgUuyQIXe_RAvarnIGhkEA'


class MyAPi(APIView):
    @staticmethod
    def get(request, message_id=9):
        message = Message.objects.all().first()
        data = {
            "id": 1,
            "phone": 384758748,
            "text": message.mailing.text
        }
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.post('https://probe.fbrq.cloud/v1/send/1', json=data, headers=headers)

        # Проверяем код состояния ответа
        if response.status_code == 200:
            message.status = 'Доставлено'
            message.save()
            return Response({'data': response.json()})
        else:
            message.status = 'Не отправлено'
            message.save()
            return Response({'data': response.status_code})


