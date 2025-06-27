from midtrans.telegram_notify import notify_admin_ebook_paid, notify_user_ebook_paid

async def handle_ebook_payment(body: dict, transaction: dict):
    await notify_admin_ebook_paid(body, transaction)
    await notify_user_ebook_paid(body, transaction)

prefix_handler_map = {
    "EBOOK": handle_ebook_payment,
}

