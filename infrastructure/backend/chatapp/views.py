from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from .pipeline import shared_pipeline
# Create your views here.


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


class TrainView(DebugabbleView):
    permission_classes = (IsAdminUser,)

    def get(self, request, format='json'):
        if shared_pipeline.trainer.getNextSetSize() > 0:
            shared_pipeline.trainer.train()
            return Response({"current_round": shared_pipeline.trainer.round})
        return Response({"error": "Don't have any data to train with"})
