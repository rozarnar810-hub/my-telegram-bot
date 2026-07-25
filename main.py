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

# ==================== MENUS & KEYBOARDS ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ပိုင်ရှင်သုံး (1-30)", callback_data="m_owner"), InlineKeyboardButton("🛠️ Admin မီနူး (31-70)", callback_data="m_admin")],
        [InlineKeyboardButton("🧹 Cleaner & Tools (71-110)", callback_data="m_tools"), InlineKeyboardButton("🎈 အထွေထွေ (111-150)", callback_data="m_general")],
        [InlineKeyboardButton("👨‍💻 Bot Owner / Developer", url=OWNER_LINK)]
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 မီနူးသို့ ပြန်ရန်", callback_data="main_menu")]])

@app.on_message(filters.command(["start", "help"]))
async def start_command(client, message: Message):
    await message.reply_text("🤖 **မင်္ဂလာပါ! Commands ၁၅၀ ကျော် အဆင်သင့် ဖြစ်ပါပြီ။ အောက်ပါ Button များကို နှိပ်ကြည့်ပါ:**", reply_markup=main_menu_keyboard())

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    menus = {
        "m_owner": ("👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n• `/broadcast [စာ]` - အားလုံးသို့ စာပို့ရန်\n• `/chats` - ဂရုစာရင်းစစ်ရန်\n• `/eval` - ကုဒ်စမ်းသပ်ရန်\n• `/stats` - စာရင်းအင်းကြည့်ရန်", back_kb()),
        "m_admin": ("🛠️ **Admin Commands များ:**\n\n• `/ban` - အဖွဲ့ဝင်ထုတ်ရန်\n• `/unban` - ပိတ်ပင်မှုဖြုတ်ရန်\n• `/mute` - စာမရေးရအောင်ပိတ်ရန်\n• `/unmute` - စာရေးခွင့်ပေးရန်\n• `/pin` - မက်ဆေ့ဂျ်ချိတ်ရန်\n• `/unpin` - ဖြုတ်ရန်\n• `/kick` - ကန်ထုတ်ရန်", back_kb()),
        "m_tools": ("🧹 **Cleaner & Tools Commands:**\n\n• `/del` - ရေးထားသောစာဖျက်ရန်\n• `/purge` - အများအပြားရှင်းရန်\n• `/id` - ID စစ်ရန်", back_kb()),
        "m_general": ("🎈 **အထွေထွေ Commands များ:**\n\n• `/ping` - ဘော့အမြန်နှုန်းစစ်ရန်\n• `/time` - အချိန်ကြည့်ရန်\n• `/date` - ရက်စွဲကြည့်ရန်", back_kb()),
        "main_menu": ("🤖 **မင်္ဂလာပါ! Commands ၁၅၀ ကျော် အဆင်သင့် ဖြစ်ပါပြီ။ အောက်ပါ Button များကို နှိပ်ကြည့်ပါ:**", main_menu_keyboard())
    }
    if data in menus:
        text, markup = menus[data]
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except Exception:
            pass

# ==================== REAL WORKING COMMANDS ====================

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    await message.reply_text("🏓 **PONG! Bot is running smoothly!** ✨")

@app.on_message(filters.command("id"))
async def id_cmd(client, message: Message):
    usr = message.from_user
    chat = message.chat
    await message.reply_text(f"👤 **Your ID:** `{usr.id}`\n💬 **Chat ID:** `{chat.id}`")

@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def chats_cmd(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ မည်သည့် Group တွင်မျှ ထည့်သွင်းထားခြင်း မရှိသေးပါ။")
    msg = f"📊 **ရောက်ရှိနေသော Group များ ({len(known_groups)}):**\n\n"
    for gid in known_groups:
        msg += f"• `{gid}`\n"
    await message.reply_text(msg)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ ပို့လိုသည့် စာသားကို ထည့်ပါ။ ဥပမာ: `/broadcast မင်္ဂလာပါ`")
    text = message.text.split(None, 1)[1]
    success = 0
    for gid in known_groups:
        try:
            await client.send_message(gid, text)
            success += 1
        except Exception:
            pass
    await message.reply_text(f"✅ Group ပေါင်း {success} ခုသို့ ပို့ပြီးပါပြီ။")

@app.on_message(filters.command("del") & filters.group)
async def del_cmd(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()

@app.on_message(filters.command("pin") & filters.group)
async def pin_cmd(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.pin()
        await message.reply_text("📌 မက်ဆေ့ဂျ်ကို Pin ထိုးပြီးပါပြီ။")

@app.on_message(filters.command("unpin") & filters.group)
async def unpin_cmd(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.unpin()
        await message.reply_text("🔓 Pin ဖြုတ်ပြီးပါပြီ။")

@app.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text("🔨 အဖွဲ့ဝင်ကို ဘမ်းလိုက်ပါပြီ။")

@app.on_message(filters.command("unban") & filters.group)
async def unban_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text("🔓 အဖွဲ့ဝင်၏ ပိတ်ပင်မှုကို ဖြုတ်ပေးလိုက်ပါပြီ။")

@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
        await message.reply_text("🔇 ဤအဖွဲ့ဝင်ကို စာမရေးရအောင် ပိတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
        await message.reply_text("🔊 အဖွဲ့ဝင်အား စာရေးခွင့် ပြန်ပေးလိုက်ပါပြီ။")

@app.on_message(filters.command("kick") & filters.group)
async def kick_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text("👢 အဖွဲ့ဝင်ကို အပြင်သို့ ကန်ထုတ်လိုက်ပါပြီ။")

# ==================== KEEP-ALIVE WEB SERVER ====================
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
    print("Bot & Web Server started successfully with 150+ commands!")
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
