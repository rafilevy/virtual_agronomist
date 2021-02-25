from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

should_exempt_csrf = csrf_exempt if settings.DEBUG else (lambda a: a)
from .views import index, insights, TrainView

app_name = 'chatapp'
urlpatterns = [
    path('', index, name='index'),
    path('insights', insights, name='insights'),
    path('train/', should_exempt_csrf(TrainView.as_view()), name="train_view"),
]
