from django.db import models
from django_cryptography.fields import encrypt


class EmailAccount(models.Model):
    """
    Аккаунты электронных почтовых ящиков.
    """
    email = models.EmailField(verbose_name='Почтовый аккаунт', unique=True)
    password = encrypt(models.CharField(verbose_name='Пароль', max_length=128))

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['email']

    def __str__(self):
        return self.email


class Email(models.Model):
    """
    Модель для хранения электронных писем.
    """
    message_id = models.CharField(
        max_length=255, verbose_name='ID письма', unique=True
    )
    mailbox = models.EmailField(verbose_name='Почтовый аккаунт')
    sender = models.EmailField(verbose_name='Отправитель')
    recipient = models.EmailField(verbose_name='Получатель', blank=True)
    subject = models.CharField(max_length=255, verbose_name='Тема', blank=True)
    sent = models.DateTimeField(verbose_name='Время отправки')
    received = models.DateTimeField(verbose_name='Время получения')
    text = models.TextField(verbose_name='Текст письма', blank=True)
    attachments = models.JSONField(verbose_name='Список вложений', blank=True)

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        ordering = ['-received']

    def __str__(self):
        return self.subject[:20]
