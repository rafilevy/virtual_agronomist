import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import asyncio

from .pipeline import shared_pipeline, ResponseRequiredException


def get_message(text, extra={}):
    return json.dumps({
        "from": True,
        "time": timezone.now(),
        "text": text,
        **extra
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
            action = text_data_json.get('action', None)
            if (action == "report"):
                await self.send(text_data=get_message(f"Question Reported", extra={"status": True}))
                texts = shared_pipeline.report(self.question)
                if texts:
                    await self.send(text_data=get_message("", extra={"options": texts}))
                else:
                    await self.send(text_data=get_message(f"Couldn't get alternative answers", extra={"status": True}))
                return
            elif (action == "correct"):
                await self.send(text_data=get_message(f"Response Recorded as Correct", extra={"status": True}))
                return
            elif (action == "answer"):
                index = int(text_data_json['index'])
                curr_in_train = shared_pipeline.processTrainingAction(
                    self.question, index)
                await self.send(text_data=get_message(f"Current # in training set {curr_in_train}", extra={"status": True}))
                return

            response = text_data_json['text']
            if self.furtherQuestion is not None:
                self.history[self.furtherQuestion] = response
                answer = shared_pipeline.answer(self.question, self.history)
            else:
                self.question = response
                answer = shared_pipeline.answer(response)
            await self.send(text_data=get_message(answer, extra={"canReport": True}))
            self.history = {}
            self.furtherQuestion = None
        except ResponseRequiredException as e:
            self.furtherQuestion = e.message
            await self.send(text_data=get_message(self.furtherQuestion))
        except Exception as e:
            print("Error processing message")
            print(str(e))
            await self.send(text_data=get_message("Error processing message!"))
