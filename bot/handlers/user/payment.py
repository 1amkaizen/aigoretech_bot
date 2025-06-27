# handlers/user/payment.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from datetime import datetime
from asyncio import get_running_loop

from telecore.logging.logger import get_logger
from telecore.midtrans.client import MidtransClient
from telecore.supabase.save_transaction import save_transaction

from .ebook import EBOOKS, safe_edit  # asumsi masih satu folder

logger = get_logger("handler.user.payment")
midtrans_client = MidtransClient()


async def ebook_beli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data_key = query.data.replace("ebook_beli_", "")
    ebook = EBOOKS.get(data_key)

    if not ebook:
        return await safe_edit(query, "🚫 Ebook tidak ditemukan.")

    # Tampilkan pilihan metode pembayaran
    buttons = [
        [InlineKeyboardButton("QRIS", callback_data=f"ebook_bayar_qris_{data_key}")],
        [InlineKeyboardButton("Virtual Account", callback_data=f"ebook_bayar_va_{data_key}")],
        [InlineKeyboardButton("E-Wallet", callback_data=f"ebook_bayar_ewallet_{data_key}")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"ebook_detail_{data_key}")]
    ]
    await safe_edit(query, "💳 *Pilih metode pembayaran:*", InlineKeyboardMarkup(buttons))


async def ebook_bayar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Format: ebook_bayar_{method}_{key}
    data = query.data.replace("ebook_bayar_", "")
    parts = data.split("_", 1)
    if len(parts) != 2:
        return await safe_edit(query, "❌ Format metode pembayaran tidak valid.")

    method, data_key = parts
    ebook = EBOOKS.get(data_key)
    if not ebook:
        return await safe_edit(query, "🚫 Ebook tidak ditemukan.")

    await safe_edit(query, f"⏳ Membuat pembayaran via *{method.upper()}*...")

    # Tentukan metode pembayaran yang diaktifkan
    payment_map = {
        "qris": ["other_qris"],
        "va": ["bank_transfer"],
        "ewallet": ["gopay", "shopeepay", "dana", "ovo"]
    }
    enabled_payments = payment_map.get(method, ["other_qris"])

    # Buat Snap Payment (bukan qris langsung!)
    user = query.from_user
    order_id = midtrans_client.generate_order_id("EBOOK")
    gross_amount = ebook["harga"]
    customer = midtrans_client.get_customer_from_user(user)

    try:
        snap_response = await midtrans_client.create_snap_payment(
            order_id=order_id,
            amount=gross_amount,
            customer=customer,
            enabled_payments=enabled_payments
        )
    except Exception as e:
        logger.exception(f"❌ Gagal membuat pembayaran: {e}")
        return await safe_edit(query, "❌ Gagal membuat pembayaran. Silakan coba lagi nanti.")

    # Simpan transaksi ke Supabase
    trx_data = {
        "order_id": order_id,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "ebook_key": data_key,
        "ebook_title": ebook["judul"],
        "gross_amount": gross_amount,
        "transaction_status": "pending",
        "payment_type": method,
        "created_at": datetime.utcnow().isoformat(),
    }

    loop = get_running_loop()
    success = await loop.run_in_executor(None, save_transaction, trx_data)
    if not success:
        return await safe_edit(query, "❌ Gagal menyimpan transaksi.")

    payment_url = snap_response.get("redirect_url", "https://app.midtrans.com/")
    logger.info(f"📦 Transaksi berhasil disiapkan untuk user {user.id} | metode: {method.upper()} | order_id: {order_id}")
    logger.info(f"🔗 Link pembayaran Midtrans: {payment_url}")

    text = (
        f"🧾 *Pembayaran Ebook*\n\n"
        f"Judul: *{ebook['judul']}*\n"
        f"Harga: Rp {gross_amount:,}".replace(",", ".") + "\n\n"
        f"Metode: `{method.upper()}`\n"
        f"Silakan tekan tombol di bawah untuk membayar:"
    )

    buttons = [
        [InlineKeyboardButton("💳 Bayar Sekarang", url=payment_url)],
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"ebook_detail_{data_key}")]
    ]
    await safe_edit(query, text, InlineKeyboardMarkup(buttons))


