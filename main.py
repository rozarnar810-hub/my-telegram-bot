import os
import json
import asyncio
import sys

# Python 3.14 Event Loop Crash Fix
if sys.version_info >= (3, 14):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = "8934169613:AAF1EdweBLj3ZRD5FA1SLJkIWu0s8sBQssE"
OWNER_ID = 7974865879
OWNER_LINK = "https://t.me/Ben_Hur_212"

app = Client("flash_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
GROUPS_FILE = "groups_list.json"

def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_groups(data):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

known_groups = load_groups()

@app.on_message(filters.group, group=-1)
async def track_groups(client, message: Message):
    if message.chat.id not in known_groups:
        known_groups.append(message.chat.id)
        save_groups(known_groups)

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ပိုင်ရှင်သုံး မီနူး", callback_data="owner_tools"), InlineKeyboardButton("📢 Tag & Mention", callback_data="tag_mention")],
        [InlineKeyboardButton("🛡️ Group လုံခြုံရေး", callback_data="group_sec"), InlineKeyboardButton("🛠️ Admin မီနူး", callback_data="admin_tools")],
        [InlineKeyboardButton("🧹 Cleaner & Tools", callback_data="cleaner"), InlineKeyboardButton("🎨 AI & Auto Reply", callback_data="ai_media")],
        [InlineKeyboardButton("🎲 ပျော်စရာဂိမ်းများ", callback_data="fun_games"), InlineKeyboardButton("🎈 အထွေထွေ မီနူး", callback_data="general")],
        [InlineKeyboardButton("👨‍💻 Bot Owner / Developer", url=OWNER_LINK)]
    ])

@app.on_message(filters.command(["start", "help"]))
async def start_command(client, message: Message):
    await message.reply_text("🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button များကို နှိပ်ပြီး အသုံးပြုနိုင်ပါတယ်:**", reply_markup=main_menu_keyboard())

@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply_text("🏓 **PONG! Bot is running smoothly!** ✨")

@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def list_chats(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ မည်သည့် Group တွင်မျှ ထည့်သွင်းထားခြင်း မရှိသေးပါ။")
    msg = f"📊 **ရောက်ရှိနေသော Group များ ({len(known_groups)}):**\n\n"
    for gid in known_groups:
        msg += f"• `{gid}`\n"
    await message.reply_text(msg)

async def handle_ping(request):
    return web.Response(text="Bot is Alive & Running 24/7!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await app.start()
    print("Bot & Web Server started successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
