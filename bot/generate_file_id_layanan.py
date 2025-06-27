import os
import json
from telegram import InputFile
from telegram.ext import Application
import asyncio

from telecore.config import BOT_TOKEN, ADMIN_ID  # Ambil dari core config

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "handlers/user/data/layanan/images")
OUTPUT_JSON = os.path.join(BASE_DIR, "handlers/user/data/layanan/file_ids.json")

def sanitize_filename(name: str) -> str:
    import re
    return re.sub(r'[^\w\d-]', '_', name.strip())

async def upload_all(app):
    result = {}
    for fname in os.listdir(IMG_DIR):
        if not fname.endswith((".png", ".jpg", ".jpeg")):
            continue
        filepath = os.path.join(IMG_DIR, fname)
        with open(filepath, "rb") as f:
            msg = await app.bot.send_photo(chat_id=ADMIN_ID[0], photo=InputFile(f))
            key = sanitize_filename(os.path.splitext(fname)[0])
            file_id = msg.photo[-1].file_id
            result[key] = file_id
            print(f"{key} => {file_id}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ file_ids.json berhasil disimpan di: {OUTPUT_JSON}")

if __name__ == "__main__":
    async def main():
        app = Application.builder().token(BOT_TOKEN).build()
        await upload_all(app)

    asyncio.run(main())

