from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .views import index
should_exempt_csrf = csrf_exempt if settings.DEBUG else (lambda a: a)

app_name = 'chatapp'
urlpatterns = [
    path('' if settings.DEBUG else 'index.html', index, name='index'),
]
