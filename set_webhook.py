# set_webhook.py
import os
from dotenv import load_dotenv
load_dotenv()  # <== penting agar .env terbaca

from telecore.config import BOT_TOKEN, WEBHOOK_URL
import requests

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    data={"url": WEBHOOK_URL}
)
print(r.json())

