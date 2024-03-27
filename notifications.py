import logging
from abc import ABC, abstractmethod
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import SETTINGS
from main import *


class BaseNotification(ABC):
    @abstractmethod
    def send_notification(self, message):
        pass


class TelegramNotification(BaseNotification):
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.webhook_url = os.environ.get(
            'TELEGRAM_WEBHOOK_URL')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.methods = {
            "get_updates": "/getUpdates",
            "send_message": "/sendMessage"
        }
        self.app = self.__get_app()

    def __get_app(self, ):
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = check_halka_arz_and_prepare_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message if message else "Bugün halka arzı olan şirket yok."
            )

        async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Sorry, I didn't understand that command.")

        app = (ApplicationBuilder().
               token(os.environ.get('TELEGRAM_BOT_TOKEN')).
               read_timeout(7).
               get_updates_read_timeout(42).build())

        start_handler = CommandHandler('start', start)
        unknown_handler = MessageHandler(filters.COMMAND, unknown)

        self.__set_web_hook(self.webhook_url)

        app.add_handler(start_handler)
        app.add_handler(unknown_handler)

        return app

    def send_notification(self, message):
        group_chat_ids = self.__get_group_chat_ids()
        for group_chat_id in group_chat_ids:
            self.__send_message(group_chat_id, message)

    def __get_group_chat_ids(self):
        group_chat_ids = os.environ.get("TELEGRAM_GROUP_CHAT_IDS")
        if group_chat_ids:
            group_chat_ids = group_chat_ids.split(",")
        return group_chat_ids

    def __send_message(self, chat_id, message_text):
        url = self.__get_url("send_message")
        params = {"chat_id": chat_id, "text": message_text}

        response = requests.post(url, data=params)
        return response

    def __get_url(self, method):
        return self.base_url + self.methods[method]

    def __set_web_hook(self, url):
        request_url = f'https://api.telegram.org/bot{self.bot_token}/setWebhook?url={url}'
        response = requests.get(request_url)
        logging.warning(response.json())


class NtfyNotification(BaseNotification):
    def __init__(self):
        self.channel_id = os.environ.get("NTFY_TOKEN")

    def send_notification(self, message):
        requests.post(f"https://ntfy.sh/{self.channel_id}",
                      data=message.encode(encoding='utf-8'))


NOTIFICATION_TYPES = {
    "telegram": TelegramNotification,
    "ntfy": NtfyNotification
}

notification_classes = [NOTIFICATION_TYPES[notification_type] for notification_type in
                        SETTINGS["ACTIVE_NOTIFICATION_TYPES"] if notification_type]
