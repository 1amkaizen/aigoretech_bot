# aigoretech_bot/urls.py
from django.contrib import admin
from django.urls import path,include
from bot.views import telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', telegram_webhook),
    path("midtrans/", include("midtrans.urls")),
]

