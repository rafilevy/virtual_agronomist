import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import asyncio

from .pipeline import shared_pipeline, ResponseRequiredException


def get_message(text):
    return json.dumps({
        "from": True,
        "time": timezone.now(),
        "text": text
    }, cls=DjangoJSONEncoder)


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = {}
        self.question = None
        self.furtherQuestion = None

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
            response = text_data_json['text']
            print("DEALING WITH RESPONSE")
            if self.furtherQuestion is not None:
                print("RESPONDING TO FURTHER QUESTION")
                self.history[self.furtherQuestion] = response
                print(self.history)
                answer = shared_pipeline.answer(self.question, self.history)
                await self.send(text_data=get_message(answer))
                self.history = {}
            else:
                self.question = response
                answer = shared_pipeline.answer(response)
                await self.send(text_data=get_message(answer))
                self.history = {}
        except ResponseRequiredException as e:
            self.furtherQuestion = e.message
            await self.send(text_data=get_message(self.furtherQuestion))
        except Exception as e:
            print("Error processing message")
            print(str(e))
            await self.send(text_data=get_message("Error processing message!"))
