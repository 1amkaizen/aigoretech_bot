import os
import json
from telegram import InputFile
from telegram.ext import Application
import asyncio
from dotenv import load_dotenv
load_dotenv()
# Ambil dari environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("ADMIN_ID")  # bisa berupa string ID atau -100...

if not BOT_TOKEN or not CHAT_ID:
    raise EnvironmentError("❌ BOT_TOKEN dan ADMIN_ID harus diset di environment variable")

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "data/ebook/images")
OUTPUT_JSON = os.path.join(BASE_DIR, "data/ebook/file_ids.json")

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
            msg = await app.bot.send_photo(
                chat_id=CHAT_ID,
                photo=InputFile(f)
            )
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

