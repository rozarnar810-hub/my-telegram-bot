import os
import json
import asyncio
import random
from datetime import datetime
from difflib import get_close_matches
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified

# Event Loop Fix
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ==================== CONFIGURATION ====================
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = "8934169613:AAF1EdweBLj3ZRD5FA1SLJkIWu0s8sBQssE"
OWNER_ID = 7974865879
OWNER_LINK = "https://t.me/Ben_Hur_212"

app = Client("flash_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MEMORY_FILE = "chat_memory.json"
GROUPS_FILE = "groups_list.json"

# ==================== DATA STORAGE ====================
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {} if "memory" in filename else []
    return {} if "memory" in filename else []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

chat_db = load_data(MEMORY_FILE)
known_groups = load_data(GROUPS_FILE)

if not isinstance(known_groups, list):
    known_groups = []

# Track Groups
@app.on_message(filters.group, group=-1)
async def track_groups(client, message: Message):
    if message.chat.id not in known_groups:
        known_groups.append(message.chat.id)
        save_data(GROUPS_FILE, known_groups)

# ==================== KEYBOARDS ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 ပိုင်ရှင်သုံး မီနူး", callback_data="owner_tools"),
            InlineKeyboardButton("📢 Tag & Mention", callback_data="tag_mention")
        ],
        [
            InlineKeyboardButton("🛡️ Group လုံခြုံရေး", callback_data="group_sec"),
            InlineKeyboardButton("🛠️ Admin မီနူး", callback_data="admin_tools")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner & Tools", callback_data="cleaner"),
            InlineKeyboardButton("🎨 AI & Auto Reply", callback_data="ai_media")
        ],
        [
            InlineKeyboardButton("🎲 ပျော်စရာဂိမ်းများ", callback_data="fun_games"),
            InlineKeyboardButton("🎈 အထွေထွေ မီနူး", callback_data="general")
        ],
        [
            InlineKeyboardButton("ℹ️ ဘော့အကြောင်း", callback_data="about"),
            InlineKeyboardButton("📜 စည်းကမ်းချက်များ", callback_data="rules")
        ],
        [
            InlineKeyboardButton("👨‍💻 Bot Owner / Developer", url=OWNER_LINK)
        ]
    ])

# ==================== COMMANDS ====================
@app.on_message(filters.command(["start", "help"]))
async def help_command(client, message: Message):
    await message.reply_text(
        "🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**",
        reply_markup=main_menu_keyboard()
    )

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Bot Owner ဖြင့် ဆက်သွယ်ရန်", url=OWNER_LINK)],
        [InlineKeyboardButton("🔙 နောက်သို့", callback_data="main_menu")]
    ])

    text_map = {
        "main_menu": ("🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**", main_menu_keyboard()),
        "owner_tools": ("👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n• `/broadcast [စာ]` - Group အားလုံးသို့ ကြော်ငြာစာပို့ရန်\n• `/chats` - Bot ရောက်နေသော Group များကို စစ်ရန်", back_button),
        "tag_mention": ("📢 **Tag & Mention Commands များ:**\n\n• `/all [စာ]` - Group မန်ဘာအားလုံးကို Tag ခေါ်ရန်\n• `/cancel` - Tag ခေါ်နေတာကို ရပ်တန့်ရန်", back_button),
        "admin_tools": ("🛠️ **Admin Commands များ:**\n\n• `/ban`, `/unban`, `/mute`, `/unmute`, `/kick`, `/pin`, `/unpin`", back_button),
        "group_sec": ("🛡️ **Group လုံခြုံရေး:** Bot ကို Admin ပေးထားပါက Group ကို စီမံပေးပါမည်။", back_button),
        "cleaner": ("🧹 **Cleaner:** `/del` - စာဖျက်ရန်", back_button),
        "ai_media": ("🎨 **Auto-Learning Reply:** စကားပြောပါက မှတ်သားထားသည်များဖြင့် ပြန်ဖြေပေးပါမည်။", back_button),
        "fun_games": ("🎲 **ဂိမ်းများ:** `/dice`, `/dart`, `/basket`, `/football`, `/slot`, `/flip`, `/rps`", back_button),
        "general": ("🎈 **အထွေထွေ:** `/id`, `/ping`, `/time`, `/date`", back_button),
        "about": (f"ℹ️ **Flash Bot**\nDeveloper: [Ben Hur]({OWNER_LINK})", back_button),
        "rules": ("📜 Group စည်းကမ်းများကို လိုက်နာပါ။", back_button)
    }

    if data == "owner_tools" and callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("⚠️ ဒီမီနူးကို Bot Owner သာ သုံးခွင့်ရှိပါတယ်!", show_alert=True)
        return

    if data in text_map:
        msg_text, markup = text_map[data]
        try:
            await callback_query.message.edit_text(msg_text, reply_markup=markup, disable_web_page_preview=True)
        except MessageNotModified:
            pass

# Owner Commands
@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def list_chats(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ Bot ကို မည်သည့် Group တွင်မျှ ထည့်သွင်းမထားသေးပါ။")
    msg = f"📊 **Bot ရောက်ရှိနေသော Group အရေအတွက်: ({len(known_groups)})**\n\n"
    for gid in known_groups:
        msg += f"• `{gid}`\n"
    await message.reply_text(msg)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ Broadcast စာကို Reply ပြန်ပါ သို့မဟုတ် စာရိုက်ထည့်ပါ။")

    success, failed = 0, 0
    await message.reply_text("🚀 ကြော်ငြာစာများ ပို့ဆောင်နေပါပြီ...")
    for gid in known_groups:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(gid)
            else:
                text = message.text.split(None, 1)[1]
                await client.send_message(gid, text)
            success += 1
            await asyncio.sleep(1)
        except Exception:
            failed += 1
    await message.reply_text(f"✅ **Broadcast ပို့ပြီးပါပြီ!**\nအောင်မြင်: `{success}` | မအောင်မြင်: `{failed}`")

# Auto Reply
@app.on_message(filters.text & ~filters.bot)
async def auto_learn_and_reply(client, message: Message):
    text = message.text.strip().lower()
    if text.startswith("/"):
        return
    if message.reply_to_message and message.reply_to_message.text:
        parent_text = message.reply_to_message.text.strip().lower()
        if not parent_text.startswith("/"):
            chat_db[parent_text] = message.text
            save_data(MEMORY_FILE, chat_db)

    matches = get_close_matches(text, chat_db.keys(), n=1, cutoff=0.45)
    if matches:
        await message.reply_text(chat_db[matches[0]])

# ==================== KEEP-ALIVE WEB SERVER (PORT FIX) ====================
async def handle_ping(request):
    return web.Response(text="Bot is Alive & Running 24/7!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    
    # Render Port Configuration (Default: 10000)
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    await start_web_server()
    await app.start()
    print("Bot & Keep-Alive Web Server started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
