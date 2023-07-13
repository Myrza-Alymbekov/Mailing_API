from rest_framework import serializers
from .models import Mailing, Client, Message, Tag


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MailingSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    total_messages = serializers.SerializerMethodField()
    sent_messages = serializers.SerializerMethodField()
    in_progress_messages = serializers.SerializerMethodField()
    not_sent_messages = serializers.SerializerMethodField()

    @staticmethod
    def get_total_messages(obj):
        return obj.message_set.count()

    @staticmethod
    def get_sent_messages(obj):
        return obj.message_set.filter(send_status='Доставлено').count()

    @staticmethod
    def get_in_progress_messages(obj):
        return obj.message_set.filter(send_status='В процессе').count()

    @staticmethod
    def get_not_sent_messages(obj):
        return obj.message_set.filter(send_status='Не отправлено').count()

    class Meta:
        model = Mailing
        fields = ('id', 'start_time', 'text', 'operator_code', 'tag', 'end_time', 'messages', 'total_messages',
                  'sent_messages', 'in_progress_messages', 'not_sent_messages')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
