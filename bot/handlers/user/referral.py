from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telecore.logging.logger import get_logger
from telecore.telegram.navigation import go_to_main_menu

logger = get_logger("handler.user.referral")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info(f"🔘 Callback 'referral' ditekan oleh user {query.from_user.id}")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main_menu")]
    ])

    await query.edit_message_text(
        "🔒 Fitur referral belum tersedia.",
        reply_markup=keyboard
    )

