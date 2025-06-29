# lib/midtrans.py

import os
import httpx
import base64
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")
MIDTRANS_URL = "https://app.sandbox.midtrans.com/snap/v1/transactions"
GROUP_VIP_ID = os.getenv("GROUP_VIP_ID")
if not MIDTRANS_SERVER_KEY:
    raise RuntimeError("❌ MIDTRANS_SERVER_KEY tidak ditemukan di .env")

# Encode key ke base64 → format: "<server_key>:"
basic_auth = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()

async def create_midtrans_transaction(
    order_id: str,
    gross_amount: int,
    customer_name: str,
    customer_email: str,
    enabled_payments: list[str] | None = None  # 👈 Tambahkan parameter opsional
):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {basic_auth}"
    }

    payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": gross_amount
        },
        "customer_details": {
            "first_name": customer_name,
            "email": customer_email
        }
    }

    # Kalau enabled_payments dikirim dari handler → override default
    if enabled_payments:
        payload["enabled_payments"] = enabled_payments
    else:
        # Default: semua metode diaktifkan
        payload["enabled_payments"] = ["gopay", "qris", "bank_transfer"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(MIDTRANS_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["redirect_url"], data
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Midtrans HTTP error: {e.response.status_code} - {e.response.text}")
        raise RuntimeError(f"❌ Midtrans HTTP error: {e}")
    except Exception as e:
        logger.exception("❌ Gagal membuat transaksi Midtrans")
        raise RuntimeError(f"❌ Midtrans error: {e}")

async def add_user_to_vip_group(user_id: int):
    try:
        await bot.invite_chat_member(chat_id=GROUP_VIP_ID, user_id=user_id)
        logging.info(f"✅ User {user_id} berhasil ditambahkan ke grup VIP")
    except Exception as e:
        logging.exception(f"❌ Gagal menambahkan user {user_id} ke grup VIP")

