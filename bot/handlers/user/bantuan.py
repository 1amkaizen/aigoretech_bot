# handlers/user/bantuan.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telecore.logging.logger import get_logger
from telecore.config import ADMIN_USERNAME

logger = get_logger("handler.user.bantuan")


ADMIN_CONTACT_URL = f"https://t.me/{ADMIN_USERNAME}"


# Tombol navigasi horizontal
def get_bantuan_nav_buttons():
    return [
        InlineKeyboardButton("📘 Ebook", callback_data="bantuan_ebook"),
        InlineKeyboardButton("🌐 Hosting", callback_data="bantuan_hosting"),
        InlineKeyboardButton("🤝 Referral", callback_data="bantuan_referral"),
    ]

back_button = [InlineKeyboardButton("⬅️ Kembali", callback_data="back_to_main")]
hubungi_admin_button = [InlineKeyboardButton("💬 Hubungi Admin", url=ADMIN_CONTACT_URL)]


async def bantuan_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"🆘 User {update.effective_user.id} membuka menu bantuan")

    keyboard = [
        get_bantuan_nav_buttons(),
        hubungi_admin_button,
        back_button
    ]

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="🆘 *Pilih topik bantuan:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def bantuan_ebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=(
            "📘 *Panduan Beli Ebook:*\n\n"
            "1. Klik menu 📘 *Ebook*\n"
            "2. Tekan tombol 'Beli Ebook Sekarang'\n"
            "3. Lakukan pembayaran via QRIS/VA\n"
            "4. Setelah berhasil, kamu akan mendapat link unduhan\n\n"
            "_Kamu juga bisa beli lewat https://clicky.id/aigoretech jika ingin cepat._"
        ),
        reply_markup=InlineKeyboardMarkup([
            get_bantuan_nav_buttons(),
            hubungi_admin_button,
            back_button
        ]),
        parse_mode="Markdown"
    )


async def bantuan_hosting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=(
            "🌐 *Panduan Beli Hosting:*\n\n"
            "1. Klik menu 🌐 *Hosting*\n"
            "2. Pilih kategori: Web, VPS, atau Cloud\n"
            "3. Pilih durasi & paket\n"
            "4. Lakukan pembayaran\n"
            "5. Link pembelian via affiliate akan dikirim\n\n"
            "_Jika ada pertanyaan, hubungi admin._"
        ),
        reply_markup=InlineKeyboardMarkup([
            get_bantuan_nav_buttons(),
            hubungi_admin_button,
            back_button
        ]),
        parse_mode="Markdown"
    )


async def bantuan_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=(
            "🤝 *Program Referral masih dalam pengembangan.*\n\n"
            "Segera hadir untuk kamu yang ingin dapat penghasilan dari promosi produk digital ini!"
        ),
        reply_markup=InlineKeyboardMarkup([
            get_bantuan_nav_buttons(),
            hubungi_admin_button,
            back_button
        ]),
        parse_mode="Markdown"
    )

