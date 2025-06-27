# bot/telegram_bot.py

from telegram.ext import ApplicationBuilder,CallbackQueryHandler

from telecore.config import BOT_TOKEN
 

application = ApplicationBuilder().token(BOT_TOKEN).build()

# Tambah dulu semua handler spesifik
from bot.handlers.user import ebook
for handler in ebook.get_handler():
    application.add_handler(handler)

application.add_handler(CallbackQueryHandler(ebook.ebook, pattern="^ebook$"))
application.add_handler(CallbackQueryHandler(ebook.ebook_detail, pattern="^ebook_detail_"))
application.add_handler(CallbackQueryHandler(ebook.ebook_faq, pattern="^ebook_faq_"))
application.add_handler(CallbackQueryHandler(ebook.ebook_faq_detail, pattern="^faq_isi_"))

# Baru tambahkan handler global tombol
from bot.handlers.user import start
for handler in start.get_handler():
    application.add_handler(handler)



from bot.handlers.user import hosting
for handler in hosting.get_handler():
    application.add_handler(handler)


