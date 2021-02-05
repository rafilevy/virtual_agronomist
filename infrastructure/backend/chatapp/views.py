from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
# Create your views here.


def index(request):
    return render(request, 'chatapp/index.html', context={})


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class DebugabbleView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication) if settings.DEBUG else (
        SessionAuthentication, BasicAuthentication)
