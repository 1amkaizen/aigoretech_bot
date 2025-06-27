# midtrans/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telecore.midtrans.webhook import handle_midtrans_webhook
from telecore.supabase.client import SupabaseClient
from .handlers import prefix_handler_map

supabase = SupabaseClient().client

@csrf_exempt
async def midtrans_webhook_view(request):
    result = await handle_midtrans_webhook(
        request=request,
        supabase_client=supabase,
        transactions_table="Transactions",
        prefix_handler_map=prefix_handler_map
    )
    return JsonResponse(result)

