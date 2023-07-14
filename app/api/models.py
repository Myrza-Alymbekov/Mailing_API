from django.db import models


TIMEZONE_CHOICES = (
    ('Europe/Kaliningrad', 'Калининград - UTC+2'),
    ('Europe/Moscow', 'Москва - UTC+3'),
    ('Europe/Samara', 'Самара - UTC+4'),
    ('Asia/Yekaterinburg', 'Екатеринбург - UTC+5'),
    ('Asia/Omsk', 'Омск - UTC+6'),
    ('Asia/Novosibirsk', 'Новосибирск - UTC+7'),
    ('Asia/Irkutsk', 'Иркутск - UTC+8'),
    ('Asia/Yakutsk', 'Якутск - UTC+9'),
    ('Asia/Vladivostok', 'Владивосток - UTC+10'),
    ('Asia/Magadan', 'Магадан - UTC+11'),
    ('Asia/Srednekolymsk', 'Среднеколымск - UTC+11'),
    ('Asia/Kamchatka', 'Петропавловск-Камчатский - UTC+12'),
)

OPERATOR_CHOICES = (
        ('', 'Выберите оператор'),
        ('900', 'Билайн (900)'),
        ('901', 'МТС (901)'),
        ('902', 'Мегафон (902)'),
        ('903', 'Теле2 (903)'),
    )


class Tag(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название Тега')

    def __str__(self):
        return f"Tag {self.id} - {self.title}"

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Mailing(models.Model):
    start_time = models.DateTimeField(verbose_name="Дата и Время Запуска")
    text = models.TextField(verbose_name='Текст сообщения')
    operator_code = models.CharField(max_length=3, choices=OPERATOR_CHOICES, verbose_name='Код Оператора')
    tag = models.ManyToManyField(Tag, verbose_name='Теги')
    end_time = models.DateTimeField(verbose_name='Дата и Время Окончания')

    def __str__(self):
        return f"Mailing {self.id} - {self.text[:30]}"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Client(models.Model):
    phone_number = models.CharField(max_length=7, verbose_name='Номер Телефона')
    operator_code = models.CharField(max_length=3, choices=OPERATOR_CHOICES, verbose_name='Код Оператора')
    tag = models.ManyToManyField(Tag, verbose_name='Теги')
    timezone = models.CharField(max_length=100, choices=TIMEZONE_CHOICES, verbose_name='Часовой Пояс')

    def __str__(self):
        return f"Client {self.id}"

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    creation_time = models.DateTimeField(verbose_name='Дата Создания')
    STATUS_CHOICES = (
        ('Не отправлено', 'Не отправлено'),
        ('В процессе', 'В процессе'),
        ('Доставлено', 'Доставлено'),
    )
    send_status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='В процессе',
                                   verbose_name='Статус Сообщения')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')

    def __str__(self):
        return f"Message {self.id} - {self.send_status}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
