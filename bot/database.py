# database.py

import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
import logging

load_dotenv()
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    raise RuntimeError(f"❌ Gagal menghubungkan ke Supabase: {e}")


async def upsert_user(user_id: int, username: str, full_name: str):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    data = {
        "user_id": user_id,
        "username": username or "",
        "full_name": full_name or "",
        "is_vip": False,
        "vip_since": None,
        "created_at": datetime.utcnow().isoformat()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/Users",
            headers=headers,
            json=[data]
        )

    # Tangani konflik duplicate user (409 Conflict)
    if response.status_code == 409:
        logger.info(f"ℹ️ User {user_id} sudah ada di database.")
        return "already_exists"

    # Tangani error lainnya
    if response.status_code not in (200, 201):
        logger.error(f"❌ Error upsert user: {response.text}")
        raise Exception(f"Supabase error: {response.status_code} - {response.text}")

    return "success"


