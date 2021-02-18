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


OPTIONS = [
    "There has been considerable debate as to whether winter barley needs treating for ramularia at T1: it is unlikely to be controllable at this early timing but in a traditional two-spray programme, with the second treatment applied at GS49 (first awns), there is likely to be a benefit to treating earlier than this.",
    "A three-spray programme for winter barley allows chlorothalonil (CTL) to be used with the latter two sprays, (so no requirement at T1) but if employing a two-spray programme (or three-sprays at T0, T1 and T2) then it would be wise to include chlorothalonil (CTL) at T1.",
    "For winter barley, in high disease pressure seasons (mild wet early spring) T0 sprays have been necessary. Although earlier timings in a T1/T2/T3 programme should remove the need for separate T0 treatment. ",
    "Although a three-spray programme is suggested for winter barley, a traditional two-spray approach will still give effective disease control but please note: T0 fungicides are more likely to be needed chlorothalonil (CTL) should be included at T1 if the second treatment is not applied until GS49. In all cases add a morpholine to the T0 if mildew is actively developing or if rusts are present requiring rapid knockdown (e.g. Corbel 0.3 l/ha).",
    "T3: 2018 was a very low disease year but still large responses to fungicide use. Responses to T3 treatment have been higher in the north for some time but responses are still high generally."
]


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
                await self.send(text_data=get_message("", extra={"options": OPTIONS}))
                return
            elif (action == "answer"):
                index = int(text_data_json['index'])
                await self.send(text_data=get_message(f"Chosen answer: {OPTIONS[index]}", extra={"status": True}))
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
        except ResponseRequiredException as e:
            self.furtherQuestion = e.message
            await self.send(text_data=get_message(self.furtherQuestion))
        except Exception as e:
            print("Error processing message")
            print(str(e))
            await self.send(text_data=get_message("Error processing message!"))
