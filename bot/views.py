# bot/views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from bot.telegram_bot import application
import json
import asyncio

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            update = Update.de_json(data, application.bot)

            async def process():
                await application.initialize()
                await application.process_update(update)
                await application.shutdown()  # agar loop bersih

            asyncio.run(process())

            return JsonResponse({"status": "ok"})
        except Exception as e:
            print("❌ Error processing update:", e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return HttpResponse("Invalid", status=400)

