# midtrans/handlers.py
from telecore.supabase.save_download_link import save_download_link
from midtrans.telegram_notify import notify_admin_ebook_paid, notify_user_ebook_paid

async def handle_ebook_payment(body: dict, transaction: dict):
    user_id = transaction.get("user_id")
    ebook_key = transaction.get("ebook_key")

    # Generate dan simpan link
    download_url = save_download_link(user_id, ebook_key)

    # Tambahkan link ke transaction dict agar bisa dikirim ke user
    transaction["download_url"] = download_url or "https://example.com/fallback"

    await notify_admin_ebook_paid(body, transaction)
    await notify_user_ebook_paid(body, transaction)

prefix_handler_map = {
    "EBOOK": handle_ebook_payment,
}

