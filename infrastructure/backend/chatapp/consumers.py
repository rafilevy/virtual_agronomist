import json
import sys
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import asyncio

from .pipeline import shared_pipeline
from .further_question_generator import ResponseRequiredException
from .pressure_score_generator import ChoiceRequiredException
from .models import PreTrainingData, RequestRecord


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
        self.saved_answer = None

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
                if type(self.saved_answer) is not str:
                    await database_sync_to_async(PreTrainingData.objects.create)(
                        **shared_pipeline.trainer.getCorrectDict(self.question, self.saved_answer)
                    )
                return
            elif (action == "answer"):
                index = int(text_data_json['index'])
                data = shared_pipeline.processTrainingAction(
                    self.question, index)
                if data is not None:
                    await database_sync_to_async(PreTrainingData.objects.create)(**data)
                    await self.send(text_data=get_message(f"Added to pre-screened training data", extra={"status": True}))
                else:
                    await self.send(text_data=get_message(f"Ignoring...", extra={"status": True}))
                return

            response = text_data_json['text']
            if self.furtherQuestion is not None:
                self.history[self.furtherQuestion] = response
                answer = shared_pipeline.answer(self.question, self.history)
            else:
                self.question = response
                await database_sync_to_async(RequestRecord.objects.create)(
                    question=response,
                    extracted=json.dumps({})
                )
                answer = shared_pipeline.answer(response)
            self.saved_answer = answer
            text = answer if type(answer) is str else answer.text
            await self.send(text_data=get_message(text, extra={"canReport": True}))
            self.history = {}
            self.furtherQuestion = None
        except ResponseRequiredException as e:
            self.furtherQuestion = e.message
            await self.send(text_data=get_message(self.furtherQuestion))
        except ChoiceRequiredException as e:
            self.furtherQuestion = e.message
            await self.send(text_data=get_message(self.furtherQuestion))
        # except Exception as e:
        #     print("Error processing message")
        #     print(str(e))
        #     print(e)
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno)
        #     await self.send(text_data=get_message("Error processing message!"))
