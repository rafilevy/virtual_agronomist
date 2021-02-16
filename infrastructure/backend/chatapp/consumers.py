import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import asyncio

from .pipeline import shared_pipeline


def get_message(text):
    return json.dumps({
        "from": True,
        "time": timezone.now(),
        "text": text
    }, cls=DjangoJSONEncoder)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONNECTED")
        await self.accept()
        await self.send(text_data=get_message("Hi, I'm the virtual agronomist, try asking me a question."))

    async def disconnect(self, close_code):
        print("DISCONNECTED")

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            answer = shared_pipeline.answer(text_data_json['text'])
            # process JSON
            await self.send(text_data=get_message(answer))
        except Exception as e:
            print("Error processing message")
            print(str(e))
            await self.send(text_data=get_message("Error processing message!"))
