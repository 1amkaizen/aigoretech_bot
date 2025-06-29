# midtrans/urls.py

from django.urls import path
from .views import midtrans_webhook_view, download_ebook, download_page

urlpatterns = [
    path("webhook/", midtrans_webhook_view, name="midtrans_webhook"),
    path("download/<uuid:token>/", download_page, name="download-page"),  # ✅ Halaman duluan
    path("download-file/<uuid:token>/", download_ebook, name="download_ebook"),  # ✅ File terpisah
]

