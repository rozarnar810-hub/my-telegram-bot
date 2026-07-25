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
TAG_TASKS = {}

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

# ==================== KEYBOARDS & MENUS ====================
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
        "admin_tools": ("🛠️ **Admin Commands များ:**\n\n• `/ban`, `/unban`, `/mute`, `/unmute`, `/kick`, `/pin`, `/unpin`, `/promote`, `/demote`", back_button),
        "group_sec": ("🛡️ **Group လုံခြုံရေး:** Bot ကို Admin ပေးထားပါက Group ကို လုံခြုံစွာ စီမံပေးပါမည်။", back_button),
        "cleaner": ("🧹 **Cleaner:**\n\n• `/del` - စာဖျက်ရန်\n• `/purge` - စာအမြောက်အများဖျက်ရန်", back_button),
        "ai_media": ("🎨 **AI & Auto Reply:** စကားပြောပါက မှတ်သားထားသည်များဖြင့် အလိုအလျောက် ပြန်ဖြေပေးပါမည်။", back_button),
        "fun_games": ("🎲 **ဂိမ်းများနှင့် ဖျော်ဖြေရေး:**\n\n• `/dice` - အန်စာတုံး လှိမ့်ရန်\n• `/dart` - မြားပစ်ရန်\n• `/basket` - ဘတ်စကတ်ဘောပစ်ရန်\n• `/football` - ဘောလုံးကန်ရန်\n• `/slot` - Slot မာရှင်ကစားရန်\n• `/flip` - အကြွေစေ့လှန်ရန်\n• `/rps` - ကျောက် ကျား စက္ကူ ကစားရန်", back_button),
        "general": ("🎈 **အထွေထွေ Commands များ:**\n\n• `/id` - ID စစ်ရန်\n• `/ping` - Bot Speed စစ်ရန်\n• `/time` & `/date` - အချိန်နှင့် ရက်စွဲကြည့်ရန်\n• `/info` - User အချက်အလက်ကြည့်ရန်", back_button),
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

# ==================== OWNER COMMANDS ====================
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

# ==================== TAG & MENTION COMMANDS ====================
@app.on_message(filters.command("all") & filters.group)
async def tag_all(client, message: Message):
    chat_id = message.chat.id
    if chat_id in TAG_TASKS and TAG_TASKS[chat_id]:
        return await message.reply_text("⚠️ Tag ခေါ်ခြင်း လုပ်ငန်းစဉ် တစ်ခု လုပ်ဆောင်ဆဲ ဖြစ်ပါသည်။")
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "📢 မန်ဘာအားလုံး အာရုံစိုက်ပေးပါဗျို့!"
    TAG_TASKS[chat_id] = True
    
    try:
        async for member in client.get_chat_members(chat_id):
            if not TAG_TASKS.get(chat_id, False):
                break
            if member.user.is_bot or member.user.is_deleted:
                continue
            await message.reply_text(f"[{member.user.first_name}](tg://user?id={member.user.id}) {text}")
            await asyncio.sleep(2)
    except Exception as e:
        await message.reply_text(f"❌ Error ဖြစ်သွားပါသည်: {e}")
    finally:
        TAG_TASKS[chat_id] = False

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message: Message):
    chat_id = message.chat.id
    if chat_id in TAG_TASKS:
        TAG_TASKS[chat_id] = False
        await message.reply_text("🛑 Tag ခေါ်ခြင်းကို ရပ်တန့်လိုက်ပါပြီ။")
    else:
        await message.reply_text("ℹ️ လက်လွှတ်စရာ Tag ခေါ်ဆိုမှု မရှိပါ။")

# ==================== ADMIN COMMANDS ====================
@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Ban မည့်သူ့စာကို Reply လုပ်ပါ။")
    user_id = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, user_id)
    await message.reply_text("🔨 အောင်မြင်စွာ Ban လိုက်ပါပြီ။")

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Unban မည့်သူ့စာကို Reply လုပ်ပါ။")
    user_id = message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply_text("🔓 အောင်မြင်စွာ Unban လိုက်ပါပြီ။")

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Mute မည့်သူ့စာကို Reply လုပ်ပါ။")
    user_id = message.reply_to_message.from_user.id
    from pyrogram.types import ChatPermissions
    await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
    await message.reply_text("🔇 ဤသူ့ကို Mute လိုက်ပါပြီ။")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Unmute မည့်သူ့စာကို Reply လုပ်ပါ။")
    user_id = message.reply_to_message.from_user.id
    from pyrogram.types import ChatPermissions
    await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=True))
    await message.reply_text("🔊 အောင်မြင်စွာ Unmute လိုက်ပါပြီ။")

@app.on_message(filters.command("pin") & filters.group)
async def pin_msg(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Pin လုပ်မည့်စာကို Reply လုပ်ပါ။")
    await message.reply_to_message.pin()
    await message.reply_text("ピン Pin ပြီးပါပြီ။")

@app.on_message(filters.command("unpin") & filters.group)
async def unpin_msg(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.unpin()
    else:
        await client.unpin_all_chat_messages(message.chat.id)
    await message.reply_text("🔓 Pin ဖြုတ်ပြီးပါပြီ။")

# ==================== CLEANER & UTILS ====================
@app.on_message(filters.command("del") & filters.group)
async def delete_msg(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()

@app.on_message(filters.command("id"))
async def get_id(client, message: Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    chat = message.chat
    await message.reply_text(f"🆔 **ID Information:**\n\n• Your ID: `{target.id}`\n• Chat ID: `{chat.id}`")

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    start = datetime.now()
    m = await message.reply_text("🏓 Pinging...")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await m.edit_text(f"🏓 **Pong!**\n⏱ Speed: `{ms} ms`")

@app.on_message(filters.command("time"))
async def time_cmd(client, message: Message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.reply_text(f"🕒 **Current Time:** `{now}`")

# ==================== FUN & GAMES ====================
@app.on_message(filters.command("dice"))
async def roll_dice(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎲")

@app.on_message(filters.command("dart"))
async def throw_dart(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎯")

@app.on_message(filters.command("basket"))
async def throw_basket(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🏀")

@app.on_message(filters.command("football"))
async def kick_football(client, message: Message):
    await client.send_dice(message.chat.id, emoji="⚽")

@app.on_message(filters.command("slot"))
async def spin_slot(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎰")

@app.on_message(filters.command("flip"))
async def flip_coin(client, message: Message):
    result = random.choice(["🪙 ခေါင်း (Heads)", "🪙 ပန်း (Tails)"])
    await message.reply_text(f"အကြွေစေ့ ရလဒ်: **{result}**")

@app.on_message(filters.command("rps"))
async def play_rps(client, message: Message):
    choices = ["ကျောက် (Rock)", "စက္ကူ (Paper)", "ကျား (Scissors)"]
    bot_choice = random.choice(choices)
    await message.reply_text(f"🤖 Bot ရွေးချယ်မှု: **{bot_choice}**")

# ==================== AI & AUTO REPLY ====================
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
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    await start_web_server()
    await app.start()
    print("Bot & Keep-Alive Web Server started successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
