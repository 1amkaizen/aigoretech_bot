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

    user = query.from_user
    await safe_edit(query, f"⏳ Membuat pembayaran via *{method.upper()}*...")

    # Metode pembayaran
    payment_map = {
        "qris": ["other_qris"],
        "va": ["bank_transfer"],
        "ewallet": ["gopay", "shopeepay", "dana", "ovo"]
    }
    enabled_payments = payment_map.get(method, ["other_qris"])

    # Persiapan Midtrans Snap
    order_id = midtrans_client.generate_order_id("EBOOK")
    gross_amount = ebook["harga"]
    customer = midtrans_client.get_customer_from_user(user)

    logger.info(f"📨 User {user.id} memilih metode: {method.upper()} | Ebook: {ebook['judul']}")
    logger.info(f"📝 Membuat order ebook: {order_id} nominal {gross_amount}, metode: {method}")

    try:
        snap_response = await midtrans_client.create_snap_payment(
            order_id=order_id,
            amount=gross_amount,
            customer=customer,
            enabled_payments=enabled_payments
        )
        logger.info(f"✅ Snap payment berhasil: {order_id}")
    except Exception as e:
        logger.exception(f"❌ Gagal membuat Snap: {e}")
        return await safe_edit(query, "❌ Gagal membuat pembayaran. Silakan coba lagi nanti.")

    # Simpan transaksi
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

    if success:
        logger.info(f"✅ Transaksi berhasil disimpan: data={trx_data}")
        logger.info(f"📦 Transaksi disimpan ke Supabase: {order_id}")
    else:
        logger.error(f"❌ Gagal simpan transaksi: {order_id}")
        return await safe_edit(query, "❌ Gagal menyimpan transaksi.")

    payment_url = snap_response.get("redirect_url", "https://app.midtrans.com/")
    logger.info(f"🔗 Link pembayaran Midtrans: {payment_url}")

    # Format invoice
    text = (
        f"🧾 *INVOICE PEMBAYARAN EBOOK*\n\n"
        f"📚 *{ebook['judul']}*\n"
        f"💵 Harga: Rp {gross_amount:,.0f}\n"
        f"💳 Metode: `{method.upper()}`\n\n"
        f"🔗 Tekan tombol di bawah untuk menyelesaikan pembayaran:"
    )

    buttons = [
        [InlineKeyboardButton("💳 Bayar Sekarang", url=payment_url)],
        [InlineKeyboardButton("❌ Batal / Kembali", callback_data=f"ebook_detail_{data_key}")]
    ]

    await safe_edit(query, text, InlineKeyboardMarkup(buttons))

