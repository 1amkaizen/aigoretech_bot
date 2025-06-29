import os
import asyncio
import logging

from django.http import (
    JsonResponse, HttpResponse, HttpResponseForbidden, StreamingHttpResponse
)
from django.views.decorators.csrf import csrf_exempt

from telecore.midtrans.webhook import handle_midtrans_webhook
from telecore.supabase.client import SupabaseClient
from .handlers import prefix_handler_map
from bot.handlers.user.ebook_file_map import EBOOK_FILE_MAP

logger = logging.getLogger("midtrans.views")
supabase = SupabaseClient().client

@csrf_exempt
def midtrans_webhook_view(request):
    logger.info("📥 Webhook diterima dari Midtrans")
    try:
        result = asyncio.run(handle_midtrans_webhook(
            request=request,
            supabase_client=supabase,
            transactions_table="Transactions",
            prefix_handler_map=prefix_handler_map
        ))
        logger.info("✅ Webhook berhasil diproses: %s", result)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("❌ Gagal memproses webhook")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

from django.http import FileResponse

from time import time

def download_ebook(request, token):
    token_str = str(token)
    logger.info("📥 Permintaan download diterima: token=%s", token_str)

    start_time = time()

    try:
        res = supabase.table("DownloadLinks").select("*").eq("token", token_str).execute()
        record = res.data[0] if res.data else None
    except Exception as e:
        logger.exception("❌ Gagal akses Supabase")
        return HttpResponse("❌ Gagal mengambil data.", status=500)

    if not record or record.get("used"):
        return HttpResponseForbidden("❌ Link tidak valid atau sudah digunakan.")

    # Tandai token sebagai digunakan
    try:
        supabase.table("DownloadLinks").update({"used": True, "used_at": "now()"}).eq("id", record["id"]).execute()
    except Exception:
        logger.exception("❌ Gagal update token")

    ebook_key = record.get("ebook_key")
    filename = EBOOK_FILE_MAP.get(ebook_key)
    file_path = f"/home/pi/aigoretech_bot/media/ebook/{filename}"

    if not filename or not os.path.exists(file_path):
        logger.error("❌ File tidak ditemukan: %s", file_path)
        return HttpResponse("❌ File tidak tersedia.", status=404)

    file_size = os.path.getsize(file_path)
    logger.info("📤 Menyiapkan file %s (%s KB)", filename, round(file_size / 1024, 2))

    try:
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
        response["Content-Length"] = str(file_size)
        duration = round(time() - start_time, 2)
        logger.info("✅ FileResponse siap dikirim (durasi=%ss)", duration)
        return response
    except Exception as e:
        logger.exception("❌ Gagal kirim file")
        return HttpResponse("❌ Terjadi kesalahan saat mengirim file.", status=500)

from django.shortcuts import render, redirect

def download_page(request, token):
    logger.info("🔍 Menampilkan halaman download untuk token=%s", token)

    try:
        res = supabase.table("DownloadLinks").select("*").eq("token", str(token)).execute()
        record = res.data[0] if res.data else None
    except Exception:
        logger.exception("❌ Gagal ambil token dari Supabase")
        return HttpResponse("Gagal memuat halaman.", status=500)

    if not record or record.get("used"):
        logger.warning("⚠️ Token tidak ditemukan atau sudah digunakan: %s", token)
        return HttpResponseForbidden("Link tidak valid atau sudah digunakan.")

    logger.info("✅ Token valid. Menampilkan halaman download.")
    return render(request, "midtrans/download_page.html", {"token": token})

