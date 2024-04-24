from config import config as cf
from django import forms
from django.contrib import admin

from .models import Email, EmailAccount


class EmailAccountForm(forms.ModelForm):
    class Meta:
        model = EmailAccount
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)
    form = EmailAccountForm


class EmailAdmin(admin.ModelAdmin):
    list_display = (
        'mailbox', 'short_subject', 'sender', 'recipient',
        'received', 'display_attachments',
    )
    search_fields = ('sender', 'subject', 'received', 'attachments')
    list_filter = ('mailbox', 'sender', 'recipient', 'received')

    def short_subject(self, obj):
        if len(obj.subject) == 0:
            return 'No subject'
        return (
            (obj.subject[:cf.ADM_SHORT_SUB] + '...')
            if len(obj.subject) > cf.ADM_SHORT_SUB
            else obj.subject
        )
    short_subject.short_description = 'Тема'

    def display_attachments(self, obj):
        if obj.attachments == []:
            return 'No attachments'
        return obj.attachments
    display_attachments.short_description = 'Вложения'


admin.site.register(EmailAccount, EmailAccountAdmin)
admin.site.register(Email, EmailAdmin)
