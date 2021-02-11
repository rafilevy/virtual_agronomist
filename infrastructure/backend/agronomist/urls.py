from django.conf.urls import include  # noqa
from django.urls import path
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("", include("chatapp.urls"), name="game"),
]
