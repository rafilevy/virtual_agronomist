from django.urls import path, include
from .views import index, insights

app_name = 'chatapp'
urlpatterns = [
    path('', index, name='index'),
    path('insights', insights, name='insights'),
]
