# midtrans/telegram_notify.py

import asyncio
from datetime import datetime
import pytz
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telecore.config import ADMIN_ID, BOT_TOKEN
from telecore.telegram.utils import send_telegram_message
from telecore.logging.logger import get_logger

logger = get_logger("midtrans.telegram_notify")
bot = Bot(token=BOT_TOKEN)

async def notify_admin_ebook_paid(body: dict, transaction: dict):
    iso_time = transaction.get("transaction_time")
    tanggal_str = waktu_str = "-"
    if iso_time:
        try:
            dt = datetime.fromisoformat(iso_time)
            dt = dt.astimezone(pytz.timezone("Asia/Jakarta"))
            tanggal_str = dt.strftime("%d %B %Y")
            waktu_str = dt.strftime("%H:%M WIB")
        except Exception as e:
            logger.warning(f"⚠️ Gagal parse waktu: {e}")

    text = (
        "✅ *PEMBAYARAN BERHASIL (EBOOK)*\n\n"
        f"*🧾 Judul*        : {transaction.get('ebook_title', '-')}\n"
        f"*👤 Nama*         : {transaction.get('full_name', '-')}\n"
        f"*🆔 User ID*      : `{transaction.get('user_id')}`\n"
        f"*💳 Metode*       : `{transaction.get('payment_type', '-')}`\n"
        f"*💰 Jumlah*       : Rp {int(transaction.get('gross_amount', 0)):,}".replace(",", ".") + "\n"
        f"*📅 Tanggal*      : {tanggal_str}\n"
        f"*⏰ Waktu*        : {waktu_str}\n"
        f"*🧾 Order ID*     : `{transaction.get('order_id', '-')}`\n"
        f"*🪪 Status*       : `{transaction.get('transaction_status', '-')}`"
    )

    for admin_id in ADMIN_ID:
        try:
            logger.info(f"📨 Mengirim notifikasi ke admin {admin_id}")
            await send_telegram_message(admin_id, text, parse_mode="Markdown")
            logger.info(f"✅ Notifikasi berhasil dikirim ke admin {admin_id}")
        except Exception as e:
            logger.warning(f"❌ Gagal kirim notifikasi ke admin {admin_id}: {e}")

async def notify_user_ebook_paid(body: dict, transaction: dict):
    user_id = transaction.get("user_id")
    title = transaction.get("ebook_title", "Ebook")
    download_link = transaction.get("download_url", "https://example.com/download/ebook")

    text = (
        f"📥 *Pembayaran Berhasil!*\n\n"
        f"Terima kasih telah membeli *{title}*.\n\n"
        f"Silakan klik tombol di bawah untuk mengunduh ebook kamu.\n\n"
        f"*Catatan:* Link hanya bisa digunakan satu kali."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download Ebook", url=download_link)]
    ])

    try:
        logger.info(f"📨 Mengirim notifikasi ke user {user_id} | Link: {download_link}")
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )
        logger.info(f"✅ Notifikasi berhasil dikirim ke user {user_id}")
    except Exception as e:
        logger.warning(f"❌ Gagal kirim notifikasi ke user {user_id}: {e}")

