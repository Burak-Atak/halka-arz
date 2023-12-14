from abc import ABC, abstractmethod
import requests
import os


class BaseNotification(ABC):
    @abstractmethod
    def send_notification(self, message):
        pass


class TelegramNotification(BaseNotification):
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.methods = {
            "get_updates": "/getUpdates",
            "send_message": "/sendMessage"
        }

    def send_notification(self, message):
        group_chat_ids = self.__get_group_chat_ids()
        for group_chat_id in group_chat_ids:
            self.__send_message(group_chat_id, message)

    def __get_group_chat_ids(self):
        url = self.__get_url("get_updates")
        updates = requests.get(url)
        print(updates.json())
        results = updates.json()["result"]

        group_chat_ids = {update["message"]["chat"]["id"] for update in results}
        return group_chat_ids

    def __send_message(self, chat_id, message_text):
        url = self.__get_url("send_message")
        params = {"chat_id": chat_id, "text": message_text}

        response = requests.post(url, data=params)
        return response

    def __get_url(self, method):
        return self.base_url + self.methods[method]


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
