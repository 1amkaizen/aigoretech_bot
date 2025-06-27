# handlers/user/ebook.py

import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackQueryHandler
from telecore.logging.logger import get_logger
from bot.handlers.user.menus import get_main_menu_rows
from telecore.telegram.navigation import go_to_main_menu
from telecore.telegram.menus import make_menu

from telecore.midtrans.client import MidtransClient
from telecore.supabase.save_transaction import save_transaction
from telecore.config import ADMIN_ID
from datetime import datetime
from asyncio import get_running_loop
    

logger = get_logger("handler.user.ebook")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
JSON_EBOOK_PATH = os.path.join(os.path.dirname(__file__), "data/ebook/ebooks.json")
FILE_ID_PATH = os.path.join(os.path.dirname(__file__), "data/ebook/file_ids.json")

try:
    with open(FILE_ID_PATH, "r", encoding="utf-8") as f:
        FILE_ID_MAP = json.load(f)
except Exception as e:
    logger.warning(f"⚠️ Gagal memuat file_ids.json: {e}")
    FILE_ID_MAP = {}

try:
    with open(JSON_EBOOK_PATH, "r", encoding="utf-8") as f:
        EBOOKS = json.load(f)
except Exception as e:
    logger.warning(f"⚠️ Gagal memuat ebooks.json: {e}")
    EBOOKS = {}

# ✅ Helper universal untuk edit caption atau text
async def safe_edit(query, text: str, reply_markup=None):
    if query.message.photo:
        await query.edit_message_caption(
            caption=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

def get_ebook_list_buttons():
    buttons = []
    for key, data in EBOOKS.items():
        buttons.append([InlineKeyboardButton(f"📘 {data['judul']}", callback_data=f"ebook_detail_{key}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

async def ebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"📚 User {update.effective_user.id} membuka menu ebook")

    markup = get_ebook_list_buttons()
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            if query.message.text != "📚 *Pilih Ebook yang ingin kamu lihat:*" and not query.message.photo:
                await query.edit_message_text(
                    text="📚 *Pilih Ebook yang ingin kamu lihat:*",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="📚 *Pilih Ebook yang ingin kamu lihat:*",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
        except Exception as e:
            logger.warning(f"⚠️ Tidak perlu update karena konten sama: {e}")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📚 *Pilih Ebook yang ingin kamu lihat:*",
            parse_mode="Markdown",
            reply_markup=markup
        )

async def ebook_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_key = query.data.replace("ebook_detail_", "")
    data = EBOOKS.get(data_key)

    if not data:
        return await safe_edit(query, "🚫 Ebook tidak ditemukan.")

    caption = (
        f"📘 *{data['judul']}*\n\n"
        f"💰 Harga: Rp {data['harga']:,}".replace(",", ".") + "\n\n"
        f"{data['deskripsi']}"
    )

    buttons = [
        [
            InlineKeyboardButton("❓ FAQ", callback_data=f"ebook_faq_{data_key}"),
            InlineKeyboardButton("🛒 Beli Ebook", callback_data=f"ebook_beli_{data_key}")
        ],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="ebook")]
    ]

    file_id = FILE_ID_MAP.get(data['file_id_key'])
    if file_id:
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=file_id, caption=caption, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            logger.warning(f"⚠️ Gagal edit media: {e}")
            await safe_edit(query, caption, InlineKeyboardMarkup(buttons))
    else:
        await safe_edit(query, caption, InlineKeyboardMarkup(buttons))

async def ebook_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_key = query.data.replace("ebook_faq_", "")
    data = EBOOKS.get(data_key)

    if not data:
        return await safe_edit(query, "🚫 Ebook tidak ditemukan.")

    faq_list = data.get("faq", [])
    if not faq_list:
        keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data=f"ebook_detail_{data_key}")]]
        return await safe_edit(query, "📭 Ebook ini belum memiliki FAQ.", InlineKeyboardMarkup(keyboard))

    keyboard = [[InlineKeyboardButton(f"❓ {f['q']}", callback_data=f"faq_isi_{data_key}_{i}")] for i, f in enumerate(faq_list)]
    keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data=f"ebook_detail_{data_key}")])

    faq_text = f"📖 *FAQ untuk {data['judul']}*"
    await safe_edit(query, faq_text, InlineKeyboardMarkup(keyboard))

async def ebook_faq_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Benar-benar pisahkan dari belakang
    parts = query.data.rsplit("_", 1)
    if len(parts) != 2:
        return await safe_edit(query, "🚫 Format FAQ tidak valid.", InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali", callback_data="ebook")]
        ]))

    prefix, idx = parts
    data_key = prefix.replace("faq_isi_", "")

    data = EBOOKS.get(data_key)
    if not data:
        return await safe_edit(query, "🚫 Ebook tidak ditemukan.", InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali", callback_data="ebook")]
        ]))

    faq = data.get("faq", [])
    if not idx.isdigit() or int(idx) >= len(faq):
        return await safe_edit(query, "🚫 FAQ tidak ditemukan.", InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali", callback_data=f"ebook_faq_{data_key}")]
        ]))

    q = faq[int(idx)]["q"]
    a = faq[int(idx)]["a"]

    faq_text = f"❓ *{q}*\n\n{a}"
    keyboard = [[
        InlineKeyboardButton("⬅️ Kembali ke FAQ", callback_data=f"ebook_faq_{data_key}"),
        InlineKeyboardButton("📘 Detail Ebook", callback_data=f"ebook_detail_{data_key}")
    ]]
    await safe_edit(query, faq_text, InlineKeyboardMarkup(keyboard))




from telegram.ext import CallbackQueryHandler
from .payment import ebook_beli, ebook_bayar

def get_handler():
    return [
        CallbackQueryHandler(ebook, pattern="^ebook$"),
        CallbackQueryHandler(ebook_detail, pattern="^ebook_detail_"),
        CallbackQueryHandler(ebook_faq, pattern="^ebook_faq_"),
        CallbackQueryHandler(ebook_faq_detail, pattern="^faq_isi_"),
        CallbackQueryHandler(ebook_beli, pattern="^ebook_beli_"),
        CallbackQueryHandler(ebook_bayar, pattern="^ebook_bayar_"),
    ]


