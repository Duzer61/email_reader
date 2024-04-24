import asyncio
import imaplib
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from config import config as cf

from .models import EmailAccount
from .services import (find_last_message_id, get_imap_server, get_message_data,
                       get_msgnums_list, get_row, get_short_msgnums_list,
                       save_message)


class EmailConsumer(AsyncWebsocketConsumer):
    """
    Работет с websockets, принимает и обрабатывает
    электронные письма.
    """

    async def receive(self, text_data):
        """
        Принимает данные от фронта. Запускает дальайшую обработку.
        """
        text_data_json = json.loads(text_data)
        email_acc = text_data_json['email_acc']
        if email_acc:
            result = await self.get_context(email_acc)
            if result.get('display_message'):
                await self.send(json.dumps({
                    'result': result['display_message'],
                    'flag': True,
                }))

    async def get_context(self, email_acc):
        """
        Управляет обработкой писем.
        """

        await self.send(text_data=json.dumps({
            'result': cf.AUTH,
        }))
        await asyncio.sleep(0.01)
        email_pass = (
            await sync_to_async(EmailAccount.objects.get)(email=email_acc)
        ).password
        imap_server = get_imap_server(email_acc)
        if not imap_server:
            return {'display_message': cf.NO_SERVER}
        imap = imaplib.IMAP4_SSL(imap_server)
        try:
            imap.login(email_acc, email_pass)
        except Exception:
            return {'display_message': cf.AUTH_ERROR}
        await self.send(text_data=json.dumps({
            'result': cf.SEARCH_START,
        }))
        await asyncio.sleep(0.5)
        msgnums_list, flag = get_msgnums_list(imap)
        if not flag:
            imap.logout()
            return {'display_message': cf.MESSAGE_LIST_ERROR}
        last_message_id = await find_last_message_id(email_acc)
        if last_message_id:
            msgnums_list = await self.find_new_messages(
                imap, msgnums_list, last_message_id
            )
            await asyncio.sleep(0.01)
        if not msgnums_list:
            return {'display_message': cf.NO_EMAILS}
        result = await self.handle_messages(imap, msgnums_list, email_acc)
        return {'display_message': result}

    async def handle_messages(self, imap, msgnums_list, email_acc):
        """
        Обрабатывает и сохраняет новые письма.
        """
        saved_messages_count = 0
        all_messages_num = len(msgnums_list)
        if all_messages_num:
            await self.send(
                text_data=json.dumps({'result': cf.LOADING})
            )
            await asyncio.sleep(0.01)
        for msgnum in msgnums_list:
            message_data = get_message_data(msgnum, imap, email_acc)
            res = await save_message(message_data)
            if res:
                table_row = get_row(message_data)
                saved_messages_count += 1
                await self.send(text_data=json.dumps({
                    'table_row': table_row,
                }))
                await asyncio.sleep(0.01)
            progress = saved_messages_count
            await self.send(
                text_data=json.dumps(
                    {
                        'progress': progress,
                        'total': all_messages_num
                    }
                )
            )
            await asyncio.sleep(0.01)
        return f'Сохранено {saved_messages_count} писем.'

    async def find_new_messages(self, imap, msgnums_list, last_message_id):
        for i in get_short_msgnums_list(imap, msgnums_list, last_message_id):
            if type(i) is not int:
                msgnums_list = i
                return msgnums_list
            elif i % cf.MESSAGE_FREQ == 0:
                message = f'проверено писем: {i}'
                await self.send(text_data=json.dumps({
                    'result': message,
                }))
                await asyncio.sleep(0.01)
