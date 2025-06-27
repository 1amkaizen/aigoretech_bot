# handlers/user/hosting.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.handlers.user.data_hosting import HOSTING_OPTIONS
from telecore.logging.logger import get_logger

logger = get_logger("handler.user.hosting")


async def hosting_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Web Hosting", callback_data="hosting:web")],
        [InlineKeyboardButton("🖥 VPS Hosting", callback_data="hosting:vps")],
        [InlineKeyboardButton("☁️ Cloud Hosting", callback_data="hosting:cloud")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")]
    ]
    await update.callback_query.message.edit_text(
        "Pilih jenis hosting yang ingin kamu lihat:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def hosting_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("hosting:"):
        jenis_map = {
            "web": "Web Hosting",
            "vps": "VPS Hosting",
            "cloud": "Cloud Hosting"
        }
        jenis_key = data.split(":")[1]
        jenis = jenis_map.get(jenis_key)

        if not jenis or jenis not in HOSTING_OPTIONS:
            await query.edit_message_text("❌ Jenis hosting tidak dikenal.")
            return

        durasi_buttons = [
            [InlineKeyboardButton(dur, callback_data=f"hosting_durasi:{jenis_key}:{dur}")]
            for dur in HOSTING_OPTIONS[jenis].keys()
        ]
        durasi_buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="hosting")])
        await query.edit_message_text(
            f"Pilih durasi paket untuk *{jenis}*:",
            reply_markup=InlineKeyboardMarkup(durasi_buttons),
            parse_mode="Markdown"
        )

    elif data.startswith("hosting_durasi:"):
        _, jenis_key, durasi = data.split(":")
        jenis_map = {
            "web": "Web Hosting",
            "vps": "VPS Hosting",
            "cloud": "Cloud Hosting"
        }
        jenis = jenis_map.get(jenis_key)
        paket_list = HOSTING_OPTIONS.get(jenis, {}).get(durasi)

        if not paket_list:
            await query.edit_message_text("⚠️ Tidak ada paket tersedia.")
            return

        await query.edit_message_text(f"📦 Daftar paket *{jenis}* ({durasi}):", parse_mode="Markdown")

        for paket in paket_list:
            fitur_text = "\n".join([f"• {f}" for f in paket['fitur']])
            text = (
                f"📦 *{paket.get('nama', jenis)}* - {durasi}\n\n"
                f"💰 Harga: {paket['harga']}\n"
                f"🔧 Fitur:\n{fitur_text}"
            )
            keyboard = [
                [InlineKeyboardButton("🛒 Beli Sekarang", url=paket['link'])]
            ]
            await query.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        keyboard = [
            [
                InlineKeyboardButton("🔙 Kembali ke Hosting", callback_data="hosting"),
                InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main")
            ]
        ]
        await query.message.reply_text("⬆️ Kembali ke menu:", reply_markup=InlineKeyboardMarkup(keyboard))


def get_handler():
    return [
        CallbackQueryHandler(hosting_callback, pattern="^hosting(:|_durasi:)"),
    ]

