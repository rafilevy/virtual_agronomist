from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
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
