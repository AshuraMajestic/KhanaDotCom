# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification = text_data_json["notification"]

        self.send(text_data=json.dumps({"notification": notification}))
