import email
import os
import re
from datetime import datetime
from email import header

import shortuuid
from asgiref.sync import sync_to_async
from config import config as cf
from dateutil import parser
from django.conf import settings

from .models import Email

attachments_folder = settings.BASE_DIR.joinpath('attachments')

if not os.path.isdir(attachments_folder):
    os.mkdir(attachments_folder)


def get_imap_server(email_acc):
    """
    Возвращает imap-сервер.
    """
    if '@gmail.com' in email_acc:
        return 'imap.gmail.com'
    if '@yandex.ru' in email_acc:
        return 'imap.yandex.ru'
    if '@mail.ru' in email_acc:
        return 'imap.mail.ru'
    return False


def get_msgnums(imap):
    """
    Возвращает количество писем в почтовом ящике или сообщение об ошибке.
    """
    try:
        status, msgnums = imap.select('INBOX')
        if status != 'OK':
            raise Exception('Bad status: ' + status)
        msgnums = msgnums[0]
        msgnums = int(msgnums.decode('utf-8'))
    except Exception as e:
        msgnums = e
    return msgnums


def get_msgnums_list(imap):
    """
    Возвращает строку с номерами писем в почтовом ящике
    или сообщение об ошибке.
    """
    try:
        imap.select('INBOX')
        status, msgnums_list = imap.search(None, 'ALL')
        if status != 'OK':
            raise Exception('Bad status: ' + status)
        msgnums_list = msgnums_list[0].split()
        return msgnums_list, True
    except Exception as e:
        return e, False


def decode_subject(subject):
    """
    Возвращает декодированную строку.
    """
    if not subject:
        return ''
    try:
        decoded_text = str(header.make_header(header.decode_header(subject)))
        return decoded_text
    except Exception:
        return cf.SUBJECT_ERROR


def get_email(subject):
    """
    Находит в строке и возвращает email.
    """
    subject = str(subject)
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, subject):
        return subject
    start_index = subject.rfind('<')
    end_index = subject.rfind('>')
    if start_index == -1 or end_index == -1:
        return cf.UNCNOWN_EMAIL
    return subject[start_index + 1:end_index]


def recode_date(date):
    """
    Преобразует формат даты для записи в бд.
    """
    date_object = parser.parse(date)
    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S%z')
    return formatted_date


def recode_date_to_text(date):
    """
    Преобразует формат даты для вывода на страницу.
    """
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z')
    formatted_date = date.strftime('%d.%m.%Y %H:%M:%S')
    return formatted_date


def decode_text(part):
    """
    Декодирует текст письма.
    """
    try:
        charset = part.get_content_charset()
        if charset:
            text = part.get_payload(decode=True).decode(charset)
            return text
        else:
            text = part.get_payload(decode=True).decode('utf-8')
            return text
    except Exception as e:
        return f'{cf.TEXT_ERROR} {e}'


async def save_message(message_data):
    """
    Сохраняет письма в базу данных.
    """
    try:
        await sync_to_async(Email.objects.create)(**message_data)
        return True
    except Exception:
        return False


def make_unique_filename(filename):
    """
    Возвращает уникальное имя файла.
    """
    unique_name = shortuuid.uuid()[:cf.UNIQUE_LENGTH]
    ext = filename.split('.')[-1]
    if ext == '':
        ext = 'unknown'
    filename = filename[:filename.rfind('.')]
    if filename == '':
        filename = 'unnamed_file'
    filename = filename + '__' + unique_name + '.' + ext
    return filename


def save_attachments(part, attachments):
    """
    Сохраняет вложения. Формирует список вложенных файлов.
    """
    try:
        filename = str(decode_subject(part.get_filename()))
        new_filename = make_unique_filename(filename)
        file_path = f'{attachments_folder}/{new_filename}'
        with open(file_path, 'wb') as f:
            f.write(part.get_payload(decode=True))
        attachments.append(file_path)
        return
    except Exception as e:
        print(f'{cf.FILE_ERROR} {e}')


def get_content(message):
    """
    Извлекает текст и вложения из письма.
    """
    text = ''
    attachments = []
    for part in message.walk():
        content_type = part.get_content_type()
        if (
            content_type == 'text/plain'
            or content_type == 'text/html'
        ):
            text += decode_text(part)
        elif 'multipart' not in content_type:
            save_attachments(part, attachments)
    return text, attachments


async def find_last_message_id(email_acc):
    """
    Проверяет есть ли письма с данного аккаунта в базе данных.
    Возвращает id последнего письма.
    """
    obj = await sync_to_async(Email.objects.filter(mailbox=email_acc).first)()
    if obj:
        last_message_id = obj.message_id
        return last_message_id
    else:
        return False


def get_short_msgnums_list(imap, msgnums_list, last_message_id):
    """
    Возвращает количество проверенных сообщений и
    список с номерами новых писем.
    """
    counter = 0
    for i in reversed(range(len(msgnums_list))):
        msgnum = msgnums_list[i]
        _, data = imap.fetch(msgnum, '(RFC822)')
        message = email.message_from_bytes(data[0][1])
        message_id = message.get("Message-ID")
        if message_id == last_message_id:
            yield msgnums_list[i + 1:] if i + 1 < len(msgnums_list) else []
            break
        counter += 1
        yield counter
    yield msgnums_list


def get_row(message_data):
    """
    Возвращает данные для строки в таблице на странице.
    """
    row = {
        'message_id': message_data['message_id'],
        'subject': message_data['subject'][:cf.TABLE_SHORT_SUB],
        'sent': recode_date_to_text(message_data['sent']),
        'received': recode_date_to_text(message_data['received']),
        'text': message_data['text'].strip()[:cf.TABLE_SHORT_TEXT],
    }
    attachments = message_data['attachments']
    if attachments:
        attachments = ''.join(
            [
                f'<p>{attachment}</p>' for attachment in attachments
            ]
         )
    row['attachments'] = attachments
    return row


def get_message_data(msgnum, imap, email_acc):
    """
    Возвращает словарь с данными письма.
    """
    _, data = imap.fetch(msgnum, '(RFC822)')
    message = email.message_from_bytes(data[0][1])
    message_id = message.get("Message-ID")
    sender = get_email(message.get('From'))
    recipient = get_email(message.get('To'))
    sent = message.get('Date')
    sent = recode_date(sent)
    received = message.get("Received").split(";")[-1].strip()
    received = recode_date(received)
    subject = decode_subject(message.get("Subject"))
    text, attachments = get_content(message)
    message_data = {
        'message_id': message_id,
        'mailbox': email_acc,
        'subject': subject,
        'sender': sender,
        'recipient': recipient,
        'sent': sent,
        'received': received,
        'text': text,
        'attachments': attachments
    }
    return message_data
