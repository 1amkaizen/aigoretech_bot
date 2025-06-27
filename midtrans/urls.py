# midtrans/urls.py

from django.urls import path
from .views import midtrans_webhook_view

urlpatterns = [
    path("webhook/", midtrans_webhook_view, name="midtrans_webhook"),
]

