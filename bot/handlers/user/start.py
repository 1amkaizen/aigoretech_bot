# handlers/user/start.py

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler

from telecore.telegram.menus import make_menu
from telecore.telegram.navigation import go_to_main_menu
from telecore.supabase.save_user import save_user_to_db
from telecore.logging.logger import get_logger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.user.hosting import hosting_entry, hosting_callback
from bot.handlers.user import ebook, layanan
from bot.handlers.user.menus import get_main_menu_rows
from bot.handlers.user.bantuan import (
    bantuan_entry,
    bantuan_ebook,
    bantuan_hosting,
    bantuan_referral,
)
logger = get_logger("handler.user.start")


# Fungsi /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"📩 User {user.id} memulai bot dengan /start")

    # Simpan user ke Supabase
    try:
        result = await save_user_to_db(
            user_id=user.id,
            username=user.username,
            full_name=f"{user.first_name or ''} {user.last_name or ''}".strip()
        )
        if result == "already_exists":
            logger.info(f"ℹ️ User sudah terdaftar: {user.id}")
        else:
            logger.info(f"✅ User baru disimpan: {user.id}")
    except Exception as e:
        logger.error(f"❌ Gagal menyimpan user {user.id}: {e}")

    # Tampilkan menu utama
    welcome_text = (
        "👋 *Selamat datang di AigoreTech Bot!*\n\n"
        "Temukan berbagai produk digital terbaik untuk kebutuhan Anda:\n\n"
        "📚 *Ebook Premium* — Belajar lebih cepat\n"
        "💻 *Hosting Murah* — Web, VPS, hingga Cloud\n"
        "🛠️ *Layanan Jasa* — Mulai dari Fastwork\n\n"
        "Silakan pilih menu di bawah ini untuk mulai:"
    )
    reply_markup = make_menu(get_main_menu_rows())

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

    return ConversationHandler.END


# Fungsi callback tombol menu
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    logger.info(f"🔘 Callback '{data}' ditekan oleh user {query.from_user.id}")

    try:
        if data == 'ebook':
            await ebook.ebook(update, context)

        elif data == 'hosting':
            await hosting_entry(update, context)

        elif data.startswith("hosting:") or data.startswith("hosting_durasi:"):
            await hosting_callback(update, context)

        elif data == 'layanan':
            await layanan.layanan(update, context)

        elif data == 'bantuan':
            await bantuan_entry(update, context)
        elif data == "bantuan_ebook":
            await bantuan_ebook(update, context)

        elif data == "bantuan_hosting":
            await bantuan_hosting(update, context)

        elif data == "bantuan_referral":
            await bantuan_referral(update, context)
        elif data == "referral":
            await query.edit_message_text(
                "🔒 Fitur referral belum tersedia.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main")]
                ])
            )

        elif data == "back":
            await hosting_entry(update, context)

        elif data == "back_to_main":
            await go_to_main_menu(update, context, menu_rows=get_main_menu_rows())

        else:
            logger.warning(f"⚠️ Callback tidak dikenal: {data}")
            await query.edit_message_text(text="❌ Pilihan tidak dikenali.")

    except Exception as e:
        logger.error(f"❌ Error saat menangani callback '{data}' oleh user {query.from_user.id}: {e}")
        await query.edit_message_text(text="🚨 Terjadi kesalahan saat memproses permintaan Anda.")

    return ConversationHandler.END


# Register handler utama
def get_handler():
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(button_callback)
    ]

