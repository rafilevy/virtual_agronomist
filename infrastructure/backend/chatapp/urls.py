from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.routers import DefaultRouter

should_exempt_csrf = csrf_exempt if settings.DEBUG else (lambda a: a)
from .views import index, insights, TrainView, FeedbackView, DataUpdateView, TableListView, DocumentListView, ReLoadDocumentsView


router = DefaultRouter()
router.register(r'table', TableListView, basename="TableWrapper")
router.register(r'document', DocumentListView, basename="DocumentWrapper")

app_name = 'chatapp'
urlpatterns = [
    path('', index, name='index'),
    path('insights/', insights, name='insights'),
    path('train/', should_exempt_csrf(TrainView.as_view()), name="train_view"),
    path('reload/', should_exempt_csrf(TrainView.as_view()), name="train_view"),
    path('feedback/', should_exempt_csrf(FeedbackView.as_view()),
         name="feedback_view"),
    path('data/config/', should_exempt_csrf(DataUpdateView.as_view()),
         name="data_update_view"),
    path('data/reload/', should_exempt_csrf(ReLoadDocumentsView.as_view()),
         name="data_update_view"),
    path('data/', include(router.urls)),
]
