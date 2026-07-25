import os
import json
import asyncio
import sys

# Python 3.14 အတွက် Event Loop အသစ်စတင်ပေးရန်
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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

# ==================== PERSISTENT GROUP STORAGE ====================
def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []

def save_groups(data):
    try:
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(set(data)), f, ensure_ascii=False, indent=4)
    except Exception:
        pass

known_groups = load_groups()

@app.on_raw_update()
async def raw_updates_handler(client, update, users, chats):
    global known_groups
    updated = False
    for chat_id in chats:
        for g_id in [chat_id, -chat_id, int(f"-100{chat_id}")]:
            if g_id not in known_groups and g_id < 0:
                known_groups.append(g_id)
                updated = True
    if updated:
        save_groups(known_groups)

@app.on_message(filters.group & ~filters.private, group=-1)
async def track_groups_msg(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in known_groups:
        known_groups.append(chat_id)
        save_groups(known_groups)

@app.on_chat_member_updated(group=-2)
async def track_bot_added(client, chat_member_updated):
    if chat_member_updated.new_chat_member:
        if chat_member_updated.new_chat_member.user.id == (await client.get_me()).id:
            chat_id = chat_member_updated.chat.id
            if chat_id not in known_groups:
                known_groups.append(chat_id)
                save_groups(known_groups)

# ==================== MENUS ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ပိုင်ရှင်သုံး မီနူး", callback_data="m_owner"), InlineKeyboardButton("🛠️ Admin မီနူး", callback_data="m_admin")],
        [InlineKeyboardButton("🧹 Cleaner & Tools", callback_data="m_tools"), InlineKeyboardButton("🎈 အထွေထွေ မီနူး", callback_data="m_general")],
        [InlineKeyboardButton("👨‍💻 Bot Owner / Developer", url=OWNER_LINK)]
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 မီနူးသို့ ပြန်ရန်", callback_data="main_menu")]])

@app.on_message(filters.command(["start", "help"]))
async def start_command(client, message: Message):
    await message.reply_text("🤖 **မင်္ဂလာပါ! အောက်ပါ Button များကို နှိပ်ပြီး အသုံးပြုနိုင်ပါပြီ:**", reply_markup=main_menu_keyboard())

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    menus = {
        "m_owner": ("👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n• `/broadcast [စာ]` - ဂရုအားလုံးသို့ အော်တိုကြော်ငြာပို့ရန်\n• `/chats` - ဘော့ရောက်နေသော ဂရုစာရင်းကြည့်ရန်\n• `/stats` - စာရင်းအင်းကြည့်ရန်", back_kb()),
        "m_admin": ("🛠️ **Admin Commands များ:**\n\n• `/ban` - အဖွဲ့ဝင်ထုတ်ရန်\n• `/unban` - ပိတ်ပင်မှုဖြုတ်ရန်\n• `/mute` - စာမရေးရအောင်ပိတ်ရန်\n• `/unmute` - စာရေးခွင့်ပေးရန်\n• `/pin` - မက်ဆေ့ဂျ်ချိတ်ရန်\n• `/kick` - ကန်ထုတ်ရန်", back_kb()),
        "m_tools": ("🧹 **Cleaner & Tools:**\n\n• `/del` - စာဖျက်ရန်\n• `/id` - ID စစ်ရန်", back_kb()),
        "m_general": ("🎈 **အထွေထွေ Commands များ:**\n\n• `/ping` - အမြန်နှုန်းစစ်ရန်", back_kb()),
        "main_menu": ("🤖 **မင်္ဂလာပါ! အောက်ပါ Button များကို နှိပ်ပြီး အသုံးပြုနိုင်ပါပြီ:**", main_menu_keyboard())
    }
    if data in menus:
        text, markup = menus[data]
        try:
            await callback_query.message.edit_text(text, reply_markup=markup)
        except Exception:
            pass

# ==================== WORKING COMMANDS ====================

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    await message.reply_text("🏓 **PONG! Bot is running smoothly!** ✨")

@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def chats_cmd(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ မည်သည့် Group တွင်မျှ ထည့်သွင်းထားခြင်း မရှိသေးပါ။")
    msg = f"📊 **ဘော့ရောက်ရှိနေသော Group စာရင်း ({len(known_groups)}):**\n\n"
    for gid in known_groups:
        msg += f"• ID: `{gid}`\n"
    await message.reply_text(msg)

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message: Message):
    await message.reply_text(f"📈 **Bot Statistics:**\n\n• Total Groups Connected: `{len(known_groups)}`\n• Status: `Active & Online 24/7`")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message: Message):
    text = ""
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    
    if not text:
        return await message.reply_text("⚠️ ကြော်ငြာပို့ရန် စာသားထည့်ပါ သို့မဟုတ် ပို့လိုသောစာကို Reply လုပ်ပြီး `/broadcast` ဟု ရေးပါ။")
    
    success = 0
    failed = 0
    for gid in known_groups:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(gid)
            else:
                await client.send_message(gid, text)
            success += 1
            await asyncio.sleep(0.3)
        except Exception:
            failed += 1
            
    await message.reply_text(f"✅ **ကြော်ငြာပို့ပြီးပါပြီ!**\n\n• အောင်မြင်သော ဂရု: `{success}` ခု\n• မအောင်မြင်သည်: `{failed}` ခု")

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
        await message.reply_text("🔓 ဤအဖွဲ့ဝင်၏ ပိတ်ပင်မှုကို ဖြုတ်ပေးလိုက်ပါပြီ။")

@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
        await message.reply_text("🔇 စာမရေးရအောင် ပိတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("kick") & filters.group)
async def kick_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text("👢 အဖွဲ့ဝင်ကို ကန်ထုတ်လိုက်ပါပြီ။")

# ==================== WEB SERVER & MAIN RUNNER ====================
async def handle_ping(request):
    return web.Response(text="Bot is Alive & Running 24/7!")

async def main():
    # Web Server စတင်ရန်
    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # Bot စတင်ရန်
    await app.start()
    print("Bot & Web Server started successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(main())
