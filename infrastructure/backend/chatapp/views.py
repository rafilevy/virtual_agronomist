from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from .pipeline import shared_pipeline
from .models import PreTrainingData
import json
from atomicwrites import atomic_write


def index(request):
    return render(request, 'chatapp/index.html', context={})


@login_required
def insights(request):
    return render(request, 'chatapp/admin.html', context={})


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class DebugabbleView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication) if settings.DEBUG else (
        SessionAuthentication, BasicAuthentication)


def get_training_response():
    return Response({
        "training": shared_pipeline.trainer.training,
        "count": PreTrainingData.objects.filter(seen=True).count(),
        "round": shared_pipeline.trainer.round - 1
    })


class FeedbackView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def get(self, request, format='json'):
        out = {"data": []}
        for pretrain_object in PreTrainingData.objects.filter(seen=False)[:10]:
            user_data = json.loads(pretrain_object.user_data)
            out["data"].append({"key": pretrain_object.pk, **user_data})
        return Response(out)

    def post(self, request, format='json'):
        try:
            new_choice = int(request.data["choice"])
            obj = PreTrainingData.objects.get(id=int(request.data["key"]))
            user_data = json.loads(obj.user_data)
            user_data["choice"] = new_choice
            obj.user_data = json.dumps(user_data)
            obj.seen = True
            obj.save()
        except:
            pass
        return get_training_response()

    def delete(self, request):
        try:
            obj = PreTrainingData.objects.get(id=int(request.body))
            obj.delete()
        except:
            pass
        return get_training_response()


class TrainView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def get(self, request, format='json'):
        return get_training_response()

    def post(self, request, format='json'):
        try:
            objs = PreTrainingData.objects.filter(seen=True).all()
            assert len(objs) > 0
            shared_pipeline.trainer.train(objs)
        except Exception as e:
            print(str(e))
            pass
        return get_training_response()


class DataUpdateView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def post(self, request, format='json'):
        def update_file(filename, f):
            if f not in request.FILES:
                return
            with open(filename, 'wb+', overwrite=True) as destination:
                for chunk in request.files[f].chunks():
                    destination.write(chunk)

        update_file('knowledgeBase/english_contractions.json', "parser")
        update_file('knowledgeBase/pressure_score.csv', 'pressure_score')
        update_file('knowledgeBase/categories.csv', 'categories')
        shared_pipeline.question_generator.update_components()
        return Response("OK!", status=status.HTTP_201_CREATED)
