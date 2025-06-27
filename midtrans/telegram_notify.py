# midtrans/telegram_notify.py

import asyncio
from telecore.config import ADMIN_ID, BOT_TOKEN
from telecore.telegram.utils import send_telegram_message
from telegram import Bot

bot = Bot(token=BOT_TOKEN)

async def notify_admin_ebook_paid(body: dict, transaction: dict):
    text = (
        "✅ *PEMBAYARAN BERHASIL*\n\n"
        f"*Judul*  : {transaction.get('ebook_title', '-')}\n"
        f"*User ID*: `{transaction.get('user_id')}`\n"
        f"*Nama*   : {transaction.get('full_name', '-')}\n"
        f"*Jumlah* : Rp {transaction.get('gross_amount')}\n"
        f"*OrderID*: `{transaction.get('order_id')}`"
    )

    for admin_id in ADMIN_ID:
        await send_telegram_message(admin_id, text, parse_mode="Markdown")


async def notify_user_ebook_paid(body: dict, transaction: dict):
    user_id = transaction.get("user_id")
    title = transaction.get("ebook_title", "Ebook")
    download_link = transaction.get("download_url", "https://example.com/download/ebook")  # dummy

    text = (
        f"📥 *Pembayaran Berhasil!*\n\n"
        f"Terima kasih telah membeli *{title}*.\n"
        f"Kamu bisa mengunduh ebook ini melalui tautan berikut:\n\n"
        f"[📘 Download Ebook]({download_link})"
    )

    try:
        await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"❌ Gagal kirim notifikasi ke user {user_id}: {e}")

