# handlers/user/layanan.py

import os
import re
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telecore.logging.logger import get_logger
from telecore.telegram.navigation import go_to_main_menu
from telecore.telegram.menus import make_menu
from bot.handlers.user.menus import get_main_menu_rows

logger = get_logger("handler.user.layanan")

BASE_DIR = os.path.dirname(__file__)
TXT_PATH = os.path.abspath(os.path.join(BASE_DIR, "data/layanan/fastwork.txt"))
IMG_DIR = os.path.abspath(os.path.join(BASE_DIR, "data/layanan/images"))
FILE_ID_PATH = os.path.abspath(os.path.join(BASE_DIR, "data/layanan/file_ids.json"))

# Load file_id map
try:
    with open(FILE_ID_PATH, "r", encoding="utf-8") as f:
        FILE_ID_MAP = json.load(f)
except Exception:
    FILE_ID_MAP = {}

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\d-]', '_', name.strip())

async def layanan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"🛠 User {user.id} membuka menu layanan")

    try:
        with open(TXT_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            if " - " not in line:
                continue
            parts = line.strip().rsplit(" - ", 1)
            if len(parts) != 2:
                continue
            
            title, url = parts

            filename_base = sanitize_filename(title)
            file_id = FILE_ID_MAP.get(filename_base)

            # Tambahan log debug
            logger.debug(f"🔍 Judul: {title}")
            logger.debug(f"🔑 Key hasil sanitasi: {filename_base}")
            logger.debug(f"📷 file_id ditemukan? {'✅' if file_id else '❌'}")


            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Lihat Detail", url=url)]
            ])
            caption = f"🛠 *{title}*"

            if file_id:
                try:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=file_id,
                        caption=caption,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                except Exception as img_err:
                    logger.error(f"❌ Gagal kirim file_id untuk {filename_base}: {img_err}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"{caption}\n_(Gagal tampilkan gambar)_",
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
            else:
                await update.callback_query.message.reply_text(
                    caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )

        # Setelah semua selesai, tampilkan menu utama
        welcome_text = (
            "Temukan berbagai produk digital terbaik untuk kebutuhan Anda:\n\n"
            "📚 *Ebook Premium* — Belajar lebih cepat\n"
            "💻 *Hosting Murah* — Web, VPS, hingga Cloud\n"
            "🛠️ *Layanan Jasa* — Mulai dari Fastwork\n\n"
            "Silakan pilih menu di bawah ini untuk mulai:"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_text,
            parse_mode="Markdown",
            reply_markup=make_menu(get_main_menu_rows())
        )

    except Exception as e:
        logger.error(f"❌ Gagal menampilkan layanan: {e}")
        await update.callback_query.message.reply_text("🚨 Gagal memuat daftar layanan.")

