import asyncio
# Python Event Loop Fix
asyncio.set_event_loop(asyncio.new_event_loop())

import os
import time
import random
import difflib
import markovify
from datetime import datetime, timedelta
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions

# API Credentials
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 7974865879

DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}
KNOWN_CHATS = set()
USER_WARNS = {}
NIGHT_MODE_TASKS = {}

# Global Control Flags
TAGGING_ACTIVE = {}

# Pyrogram Client
app = Client("my_tag_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🌐 Render 24/7 Keep Alive Web Server
async def handle_health_check(request):
    return web.Response(text="Bot is 24/7 Active and Running!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# 💾 Helper Functions
def save_text(text: str):
    if text and len(text.split()) >= 1 and not text.startswith("/"):
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")

def generate_smart_reply(user_message: str) -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲဗျာ။"

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            return "စကားလုံး အချက်အလက် မရှိသေးပါဗျာ။"

        matches = difflib.get_close_matches(user_message, lines, n=3, cutoff=0.3)
        if matches:
            return random.choice(matches)

        matched_lines = [l for l in lines if any(word in l for word in user_message.split() if len(word) > 2)]
        if matched_lines:
            return random.choice(matched_lines)

        text_data = "\n".join(lines)
        text_model = markovify.NewlineText(text_data, state_size=1)
        reply = text_model.make_sentence(tries=50)

        return reply if reply else random.choice(lines)
    except Exception:
        return "မင်္ဂလာပါဗျာ။"

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def parse_time(time_str: str) -> int:
    unit = time_str[-1].lower()
    value = int(time_str[:-1]) if time_str[:-1].isdigit() else 0
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    return 0

# 🔘 INTERACTIVE BUTTON UI (EXTENDED)
def get_help_buttons():
    buttons = [
        [
            InlineKeyboardButton("👑 Owner Tools", callback_data="help_owner"),
            InlineKeyboardButton("📢 Tag & Mention", callback_data="help_tagging")
        ],
        [
            InlineKeyboardButton("🛡️ Group Security", callback_data="help_security"),
            InlineKeyboardButton("🛠️ Admin Tools", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner & Night", callback_data="help_cleaner"),
            InlineKeyboardButton("🎨 AI & Media", callback_data="help_ai_media")
        ],
        [
            InlineKeyboardButton("🎲 Fun & Games", callback_data="help_games"),
            InlineKeyboardButton("🎈 General & Utility", callback_data="help_general")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 မူလ Help Menu သို့ ပြန်သွားရန်", callback_data="help_main")]])

# 🤖 BOT MAIN COMMANDS
@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    KNOWN_CHATS.add(message.chat.id)
    text = (
        "👋 **မင်္ဂလာပါ!**\n\n"
        "ကျွန်တော်ကတော့ Group မန်နေးဂျာ စနစ်၊ Admin တဂ်ခေါ်စနစ်၊ AI Auto-Chat၊ Security နဲ့ Fun Games များ အစုံအလင် ပါဝင်တဲ့ **24/7 Multi-Functional Telegram Bot** ဖြစ်ပါတယ်။\n\n"
        "👇 အောက်ပါ Button များကို နှိပ်ပြီး Command များကို လေ့လာနိုင်ပါတယ်ဗျာ။"
    )
    await message.reply_text(text, reply_markup=get_help_buttons())

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text("🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**", reply_markup=get_help_buttons())

# 🔘 BUTTON CALLBACK HANDLER
@app.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "help_main":
        await query.message.edit_text("🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**", reply_markup=get_help_buttons())

    elif data == "help_owner":
        text = (
            "👑 **Owner Only Commands**\n\n"
            "• `/broadcast [စာသား]` - Group အားလုံးသို့ ကြေညာစာ ပို့ရန်\n"
            "• `/botstats` - Bot သုံးထားသော Group နှင့် Data စာရင်း\n"
            "• `/add [စာသား]` - Bot ကို စကားသစ်များ manual သင်ပေးရန်\n"
            "• `/setchance [0-100]` - Auto ဝင်ပြောမည့် နှုန်းသတ်မှတ်ရန်\n"
            "• `/clearmemory` - မှတ်ထားသော စကားလုံးများ ရှင်းထုတ်ရန်\n"
            "• `/say [စာသား]` - Bot ကို စာပြန်ပြောခိုင်းရန်\n"
            "• `/leavechat [Chat ID]` - Bot ကို Group မှ ထွက်ခိုင်းရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_tagging":
        text = (
            "📢 **Tagging & Mention Commands**\n\n"
            "• `/admin` / `/admins` / `@admins` - **Admin အားလုံးကို Tag ခေါ်ရန်**\n"
            "• `/tagall [စာသား]` - မန်ဘာ အားလုံးကို Tag ခေါ်ရန် (Owner Only)\n"
            "• `/cancel` / `/stop` - Tag ခေါ်နေခြင်းကို ချက်ချင်း ရပ်တန့်ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_security":
        text = (
            "🛡️ **Group Security & Safeguard**\n\n"
            "• `/antilink [on/off]` - Link ပို့ပါက အလိုအလျောက် ဖျက်ရန်\n"
            "• `/welcome [on/off]` - Welcome Message ပြ/မပြ သတ်မှတ်ရန်\n"
            "• `/lock [type]` - Media ပိတ်ရန် (sticker/photo/video/link/forward/audio/voice/document)\n"
            "• `/unlock [type]` - ပိတ်ထားသော Media ပြန်ဖွင့်ရန်\n"
            "• `/warn` - User ကို သတိပေးချက် ပေးရန် (3 ကြိမ်ပြည့်ပါက Mute)\n"
            "• `/unwarn` - သတိပေးချက် ပြန်ရုပ်သိမ်းရန်\n"
            "• `/warns` - သတိပေးချက် စာရင်း ကြည့်ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_admin":
        text = (
            "🛠️ **Admin & Moderation Tools**\n\n"
            "• `/ban` / `/unban [ID]` - Ban/Unban ပြုလုပ်ရန်\n"
            "• `/tban [10m/1h]` - အချိန်သတ်မှတ်၍ Ban ထားရန်\n"
            "• `/mute` / `/unmute` - စာရိုက်ခွင့် ပိတ်/ဖွင့် ရန်\n"
            "• `/tmute [10m/1h]` - အချိန်သတ်မှတ်၍ Mute ထားရန်\n"
            "• `/kick` / `/dkick` - Group မှ ထုတ်ရန် (dkick သည် စာပါဖျက်သည်)\n"
            "• `/pin` / `/unpin` / `/unpinall` - Pin/Unpin ပြုလုပ်ရန်\n"
            "• `/settitle [အမည်]` - Admin Custom Title ပြောင်းရန်\n"
            "• `/setgtitle [အမည်]` - Group အမည် ပြောင်းရန်\n"
            "• `/setgdesc [စာသား]` - Group Description ပြောင်းရန်\n"
            "• `/adminlist` - Admin စာရင်း သီးသန့် ထုတ်ပြရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_cleaner":
        text = (
            "🧹 **Cleaner & Night Mode Tools**\n\n"
            "• `/del` - စာတစ်ကြောင်းချင်း ဖျက်ရန်\n"
            "• `/purge` - စာများကို အမြောက်အမြား ဖျက်ပစ်ရန်\n"
            "• `/zombies` - Deleted Accounts များ ရှာရန်\n"
            "• `/cleanzombies` - Deleted Accounts များကို Kick ရန်\n"
            "• `/nightmode [on/off]` - ညဘက် Group တွင် စာရိုက်ခွင့် ပိတ်/ဖွင့် ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_ai_media":
        text = (
            "🎨 **AI & Media Tools**\n\n"
            "• `/gen [Prompt]` - AI ဖြင့် ပုံဆွဲရန်\n"
            "• `/wimage [Text]` - Welcome Banner ပုံ ဖန်တီးရန်\n"
            "• `/carbon [Text]` - စာများကို Code Style Image အဖြစ် ပြောင်းရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_games":
        text = (
            "🎲 **Fun & Games Commands**\n\n"
            "• `/couples` - Group စုံတွဲ မဲနှိုက်ရန် 👩‍❤️‍👨\n"
            "• `/slap` - မန်ဘာကို ပါးရိုက်ရန် 👋\n"
            "• `/roll` - ဂဏန်း Random နှိုက်ရန် (0-100)\n"
            "• `/truth` / `/dare` - Truth or Dare မေးခွန်းများ\n"
            "• `/choose [a] [b]` - Bot ကို ရွေးချယ်ခိုင်းရန်\n"
            "• `/dice` 🎲 / `/dart` 🎯 / `/basket` 🏀\n"
            "• `/bowling` 🎳 / `/football` ⚽ / `/slot` 🎰"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_general":
        text = (
            "🎈 **General & Utility Commands**\n\n"
            "• `/ping` - Bot မြန်ဆန်မှု (Speed) စစ်ရန်\n"
            "• `/id` - User သို့မဟုတ် Group ID ကြည့်ရန်\n"
            "• `/userinfo` / `/info` - User Profile စစ်ရန်\n"
            "• `/groupinfo` - Group အချက်အလက် ကြည့်ရန်\n"
            "• `/time` - လက်ရှိ အချိန်နှင့် ရက်စွဲ ကြည့်ရန်\n"
            "• `/math [ပုစ္ဆာ]` - သင်္ချာ တွက်ချက်ရန် (ဥပမာ `/math 25*4`)\n"
            "• `/crypto [coin]` - Coin ဈေးနှုန်း စစ်ရန် (ဥပမာ `/crypto btc`)"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

# 📣 ADMIN MENTION COMMANDS (/admin, /admins, @admins)
@app.on_message(filters.command(["admin", "admins"]) | filters.regex(r"(?i)^@admins?"))
async def admin_tag_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command က Group ထဲမှာပဲ သုံးလို့ရပါတယ်ဗျာ။")
        return

    reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "အရေးကြီး အကူအညီ လိုအပ်နေပါသည်!"
    
    msg = await message.reply_text("🔍 Admins များကို ရှာဖွေခေါ်ယူနေပါသည်...")
    admin_mentions = []
    
    async for member in client.get_chat_members(message.chat.id, filter=filters.chat_members_filter.ADMINISTRATORS):
        if not member.user.is_bot:
            name = member.user.first_name if member.user.first_name else "Admin"
            admin_mentions.append(f"[{name}](tg://user?id={member.user.id})")
            
    if admin_mentions:
        text = f"🚨 **Admin များ သတိပြုရန်!**\n\n📝 **အကြောင်းအရာ:** {reason}\n\n👥 **Admins:** " + " ".join(admin_mentions)
        await msg.edit_text(text)
    else:
        await msg.edit_text("❌ Admin များ ရှာမတွေ့ပါ။")

# 🛑 TAG CANCEL COMMAND
@app.on_message(filters.command(["cancel", "stop"]))
async def cancel_tag_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    chat_id = message.chat.id
    if TAGGING_ACTIVE.get(chat_id, False):
        TAGGING_ACTIVE[chat_id] = False
        await message.reply_text("🛑 Tag ခေါ်ယူနေခြင်းကို **ရပ်တန့်လိုက်ပါပြီ**။")
    else:
        await message.reply_text("💡 အလုပ်လုပ်နေသော Tag ခေါ်ယူမှု မရှိပါ။")

# 🏷️ TAG ALL WITH CANCEL FEATURE
@app.on_message(filters.command("tagall"))
async def tagall_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command ကို Group ထဲမှာသာ အသုံးပြုနိုင်ပါတယ်ဗျာ။")
        return
    
    chat_id = message.chat.id
    TAGGING_ACTIVE[chat_id] = True

    notice = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "လူစုံတက်စုံ သတိပေးချက်!"
    status_msg = await message.reply_text("🔍 Group ထဲရှိ မန်ဘာ အားလုံးကို စစ်ဆေးနေပါသည်...")
    
    try:
        members = []
        async for member in client.get_chat_members(chat_id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)
        total_count = len(members)
        await status_msg.edit_text(f"📣 **{notice}**\n\n👥 စုစုပေါင်း မန်ဘာ **{total_count}** ယောက်အား Tag ခေါ်နေပါပြီ...\n(ရပ်ချင်ပါက `/cancel` ဟု ရိုက်ပါ)")
        
        chunk_size = 5
        for i in range(0, total_count, chunk_size):
            if not TAGGING_ACTIVE.get(chat_id, True):
                await message.reply_text("🛑 Tag ခေါ်ယူခြင်း လုပ်ငန်းစဉ် ရပ်တန့်သွားပါပြီ။")
                break
            
            chunk = members[i:i + chunk_size]
            mention_text = f"📣 **{notice}**\n"
            for user in chunk:
                name = user.first_name if user.first_name else "User"
                mention_text += f"[{name}](tg://user?id={user.id})  "
            await client.send_message(chat_id, mention_text)
            await asyncio.sleep(2)
            
    except Exception as e:
        await message.reply_text(f"❌ အမှားဖြစ်ပေါ်ပါသည်: {e}")
    finally:
        TAGGING_ACTIVE[chat_id] = False

# 🔒 LOCK & UNLOCK SYSTEM (EXTENDED)
@app.on_message(filters.command("lock"))
async def lock_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/lock [sticker/photo/video/link/forward/audio/voice/document]`")
        return
    lock_type = args[1].lower()
    CHAT_SETTINGS.setdefault(message.chat.id, {})[f"lock_{lock_type}"] = True
    await message.reply_text(f"🔒 **{lock_type.capitalize()}** ပို့ခွင့်ကို ပိတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("unlock"))
async def unlock_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/unlock [sticker/photo/video/link/forward/audio/voice/document]`")
        return
    lock_type = args[1].lower()
    CHAT_SETTINGS.setdefault(message.chat.id, {})[f"lock_{lock_type}"] = False
    await message.reply_text(f"🔓 **{lock_type.capitalize()}** ပိတ်ထားသည်ကို ပြန်ဖွင့်ပေးလိုက်ပါပြီ။")

# ⚠️ WARN SYSTEM
@app.on_message(filters.command("warn"))
async def warn_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 သတိပေးချင်သည့် User ၏ စာကို Reply ပြန်ပါ။")
        return
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    
    USER_WARNS.setdefault(chat_id, {})
    USER_WARNS[chat_id][user_id] = USER_WARNS[chat_id].get(user_id, 0) + 1
    warn_count = USER_WARNS[chat_id][user_id]
    
    if warn_count >= 3:
        try:
            await message.chat.restrict_member(user_id, ChatPermissions())
            await message.reply_text(f"⚠️ User [{message.reply_to_message.from_user.first_name}](tg://user?id={user_id}) သည် Warn 3 ကြိမ်ပြည့်သွားသဖြင့် စာရိုက်ခွင့် Mute ခံလိုက်ရပါပြီ။")
            USER_WARNS[chat_id][user_id] = 0
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
    else:
        await message.reply_text(f"⚠️ User [{message.reply_to_message.from_user.first_name}](tg://user?id={user_id}) အား သတိပေးလိုက်ပါပြီ။ ({warn_count}/3)")

@app.on_message(filters.command("unwarn"))
async def unwarn_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Warn ပြန်လျှော့ချင်သည့် User ၏ စာကို Reply ပြန်ပါ။")
        return
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    if chat_id in USER_WARNS and user_id in USER_WARNS[chat_id] and USER_WARNS[chat_id][user_id] > 0:
        USER_WARNS[chat_id][user_id] -= 1
        await message.reply_text(f"✅ User အား Warn 1 ကြိမ် လျှော့ပေးလိုက်ပါပြီ။ လက်ရှိ Warn: ({USER_WARNS[chat_id][user_id]}/3)")
    else:
        await message.reply_text("💡 ဒီ User ထံတွင် Warn မရှိပါ။")

@app.on_message(filters.command("warns"))
async def warns_cmd(client: Client, message: Message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    chat_id = message.chat.id
    warns = USER_WARNS.get(chat_id, {}).get(user.id, 0)
    await message.reply_text(f"⚠️ [{user.first_name}](tg://user?id={user.id}) ၏ သတိပေးချက် စုစုပေါင်း: ({warns}/3)")

# 🌙 NIGHT MODE
@app.on_message(filters.command("nightmode"))
async def nightmode_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() not in ["on", "off"]:
        await message.reply_text("💡 အသုံးပြုပုံ: `/nightmode on` သို့မဟုတ် `/nightmode off`")
        return
    status = args[1].lower() == "on"
    if status:
        await message.chat.set_permissions(ChatPermissions())
        await message.reply_text("🌙 **Night Mode On:** Group ထဲတွင် စာရိုက်ခွင့် ယာယီ ပိတ်လိုက်ပါပြီ။")
    else:
        await message.chat.set_permissions(ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        ))
        await message.reply_text("☀️ **Night Mode Off:** Group ထဲတွင် စာပြန်ရိုက်ခွင့် ပြုလိုက်ပါပြီ။")

# 🧮 UTILITY COMMANDS (MATH, CRYPTO, TIME, CARBON)
@app.on_message(filters.command("math"))
async def math_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/math 12 * 5` သို့မဟုတ် `/math (100-20)/2`")
        return
    expr = message.text.split(maxsplit=1)[1]
    try:
        allowed = "0123456789+-*/(). "
        if all(c in allowed for c in expr):
            res = eval(expr)
            await message.reply_text(f"🧮 **ရလဒ်:** `{res}`")
        else:
            await message.reply_text("❌ မမှန်ကန်သော သင်္ချာသင်္ကေတ ပါဝင်နေပါသည်။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("crypto"))
async def crypto_cmd(client: Client, message: Message):
    args = message.text.split()
    coin = args[1].upper() if len(args) > 1 else "BTC"
    await message.reply_text(f"🪙 **{coin}** ဈေးနှုန်း စစ်ဆေးခြင်း: လတ်တလော စနစ်ချိတ်ဆက်နေဆဲဖြစ်ပါသည်။")

@app.on_message(filters.command("time"))
async def time_cmd(client: Client, message: Message):
    now = datetime.now()
    await message.reply_text(f"🕒 **လက်ရှိ အချိန်:** {now.strftime('%Y-%m-%d %H:%M:%S')}")

@app.on_message(filters.command("carbon"))
async def carbon_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/carbon print('Hello World')`")
        return
    code_text = message.text.split(maxsplit=1)[1]
    encoded = code_text.replace(" ", "%20")
    img_url = f"https://image.pollinations.ai/prompt/code%20snippet%20editor%20dark%20theme%20with%20text%20{encoded}"
    await message.reply_photo(photo=img_url, caption="💻 **Code Snippet Image**")

# 👤 USER INFO & ADMINLIST
@app.on_message(filters.command(["userinfo", "info"]))
async def userinfo_cmd(client: Client, message: Message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    info_text = (
        f"👤 **User Information**\n\n"
        f"• **အမည်:** {user.first_name} {user.last_name or ''}\n"
        f"• **Username:** @{user.username or 'မရှိပါ'}\n"
        f"• **User ID:** `{user.id}`\n"
        f"• **Is Bot:** {'ဟုတ်ပါတယ်' if user.is_bot else 'မဟုတ်ပါ'}"
    )
    await message.reply_text(info_text)

@app.on_message(filters.command("adminlist"))
async def adminlist_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        return
    admin_list = "👥 **Group Admins စာရင်း:**\n\n"
    async for member in client.get_chat_members(message.chat.id, filter=filters.chat_members_filter.ADMINISTRATORS):
        if not member.user.is_bot:
            admin_list += f"• [{member.user.first_name}](tg://user?id={member.user.id})\n"
    await message.reply_text(admin_list)

# 🎲 EXTRA FUN & GAMES
@app.on_message(filters.command("roll"))
async def roll_cmd(client: Client, message: Message):
    num = random.randint(0, 100)
    await message.reply_text(f"🎲 **Random Number:** `{num}`")

@app.on_message(filters.command("truth"))
async def truth_cmd(client: Client, message: Message):
    questions = [
        "မင်းရဲ့ အကြီးမားဆုံး လျှို့ဝှက်ချက်က ဘာလဲ။",
        "Group ထဲမှာ ဘယ်သူ့ကို အချစ်ဆုံးလဲ။",
        "နောက်ဆုံး ငိုခဲ့ရတဲ့ အကြောင်းအရင်းက ဘာလဲ။"
    ]
    await message.reply_text(f"🤔 **Truth:** {random.choice(questions)}")

@app.on_message(filters.command("dare"))
async def dare_cmd(client: Client, message: Message):
    dares = [
        "Group ထဲမှာ စတစ်ကာ ၅ ခု ဆက်တိုက် ပို့ပါ။",
        "မင်းရဲ့ အမိုက်ဆုံး ပုံတစ်ပုံ Group ထဲ ပို့ပါ။",
        "စော်/ဘဲ ဆီ 'ငါမင်းကို လွမ်းတယ်' လို့ စာသွားပို့ပါ။"
    ]
    await message.reply_text(f"🔥 **Dare:** {random.choice(dares)}")

@app.on_message(filters.command("choose"))
async def choose_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or " " not in args[1]:
        await message.reply_text("💡 အသုံးပြုပုံ: `/choose ထမင်းစားမယ် ခေါက်ဆွဲသောက်မယ်`")
        return
    options = args[1].split()
    await message.reply_text(f"🤔 ကျွန်တော် ရွေးချယ်ပေးတာကတော့: **{random.choice(options)}** ဖြစ်ပါတယ်ဗျာ!")

@app.on_message(filters.command("say"))
async def say_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return
    if len(message.text.split()) < 2:
        return
    text = message.text.split(maxsplit=1)[1]
    await message.delete()
    await message.reply_text(text)

# 🛡️ SECURITY & GROUP SETTINGS
@app.on_message(filters.command("antilink"))
async def antilink_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() not in ["on", "off"]:
        await message.reply_text("💡 အသုံးပြုပုံ: `/antilink on` သို့မဟုတ် `/antilink off`")
        return
    status = args[1].lower() == "on"
    CHAT_SETTINGS.setdefault(message.chat.id, {})["antilink"] = status
    await message.reply_text(f"🛡️ Anti-Link စနစ်ကို **{'ဖွင့်လိုက်ပါပြီ (ON)' if status else 'ပိတ်လိုက်ပါပြီ (OFF)'}**")

@app.on_message(filters.command("welcome"))
async def welcome_setting_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() not in ["on", "off"]:
        await message.reply_text("💡 အသုံးပြုပုံ: `/welcome on` သို့မဟုတ် `/welcome off`")
        return
    status = args[1].lower() == "on"
    CHAT_SETTINGS.setdefault(message.chat.id, {})["welcome"] = status
    await message.reply_text(f"👋 Welcome Message စနစ်ကို **{'ဖွင့်လိုက်ပါပြီ (ON)' if status else 'ပိတ်လိုက်ပါပြီ (OFF)'}**")

# ⏱️ TIMED MODERATION & DKICK
@app.on_message(filters.command("dkick"))
async def dkick_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Kick ခင်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.reply_to_message.delete()
        await message.chat.ban_member(user_id)
        await message.chat.unban_member(user_id)
        await message.reply_text(f"👞 စာပါဖျက်ပြီး User `{user_id}` ကို Group မှ ထုတ်ပစ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("tmute"))
async def tmute_cmd(client: Client, message: Message):
    if not message.reply_to_message or len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: Reply ပြန်ပြီး `/tmute 10m` (10m = 10 Minutes, 1h = 1 Hour)")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        seconds = parse_time(message.text.split()[1])
        if seconds == 0:
            await message.reply_text("❌ အချိန် သတ်မှတ်မှု မှားယွင်းနေပါသည်။")
            return
        until_date = datetime.now() + timedelta(seconds=seconds)
        await message.chat.restrict_member(user_id, ChatPermissions(), until_date=until_date)
        await message.reply_text(f"🔇 User `{user_id}` အား **{message.text.split()[1]}** အတွက် စာရိုက်ခွင့် ပိတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("tban"))
async def tban_cmd(client: Client, message: Message):
    if not message.reply_to_message or len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: Reply ပြန်ပြီး `/tban 1h` (1h = 1 Hour, 1d = 1 Day)")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        seconds = parse_time(message.text.split()[1])
        if seconds == 0:
            await message.reply_text("❌ အချိန် သတ်မှတ်မှု မှားယွင်းနေပါသည်။")
            return
        until_date = datetime.now() + timedelta(seconds=seconds)
        await message.chat.ban_member(user_id, until_date=until_date)
        await message.reply_text(f"⛔️ User `{user_id}` အား **{message.text.split()[1]}** အထိ Ban လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# 🧹 CLEANER HANDLERS
@app.on_message(filters.command("purge"))
async def purge_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 ဖျက်ချင်သည့် စာ၏ စတင်ရာနေရာကို Reply ပြန်ပါ။")
        return
    start_id = message.reply_to_message.id
    end_id = message.id
    message_ids = list(range(start_id, end_id + 1))
    
    try:
        await client.delete_messages(message.chat.id, message_ids)
        msg = await message.reply_text(f"🧹 စုစုပေါင်း စာကြောင်း **{len(message_ids)}** ခုအား ရှင်းထုတ်ပြီးပါပြီ။")
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("zombies"))
async def zombies_cmd(client: Client, message: Message):
    deleted_count = 0
    msg = await message.reply_text("🔍 Deleted Accounts များကို စစ်ဆေးနေပါသည်...")
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            deleted_count += 1
    await msg.edit_text(f"🧟‍♂️ Group ထဲတွင် Deleted Accounts/Zombies စုစုပေါင်း **{deleted_count}** ခု ရှိနေပါသည်။")

@app.on_message(filters.command("cleanzombies"))
async def cleanzombies_cmd(client: Client, message: Message):
    kicked_count = 0
    msg = await message.reply_text("🧹 Deleted Accounts များကို Group မှ ရှင်းထုတ်နေပါသည်...")
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            try:
                await message.chat.ban_member(member.user.id)
                await message.chat.unban_member(member.user.id)
                kicked_count += 1
                await asyncio.sleep(0.5)
            except Exception:
                pass
    await msg.edit_text(f"✅ Deleted Accounts စုစုပေါင်း **{kicked_count}** ခုအား ရှင်းထုတ်ပြီးပါပြီ။")

# 🛠️ EXTRA GROUP SETTINGS
@app.on_message(filters.command("unpinall"))
async def unpinall_cmd(client: Client, message: Message):
    try:
        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("📌 Pin ထားသော စာများ အားလုံးကို ဖြုတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("leavechat"))
async def leavechat_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    target_chat = int(args[1]) if len(args) > 1 else message.chat.id
    await client.leave_chat(target_chat)

@app.on_message(filters.command("settitle"))
async def settitle_cmd(client: Client, message: Message):
    if not message.reply_to_message or len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: Admin ကို Reply ပြန်ပြီး `/settitle VIP Admin` ရိုက်ပါ။")
        return
    title = message.text.split(maxsplit=1)[1]
    user_id = message.reply_to_message.from_user.id
    try:
        await client.set_administrator_title(message.chat.id, user_id, title)
        await message.reply_text(f"✅ Admin ရာထူး အမည်အား **{title}** သို့ ပြောင်းလဲလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("setgtitle"))
async def setgtitle_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/setgtitle Group အမည်သစ်`")
        return
    new_title = message.text.split(maxsplit=1)[1]
    try:
        await message.chat.set_title(new_title)
        await message.reply_text(f"✅ Group အမည်ကို **{new_title}** သို့ ပြောင်းလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("setgdesc"))
async def setgdesc_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/setgdesc Group အကြောင်းအရာ`")
        return
    desc = message.text.split(maxsplit=1)[1]
    try:
        await message.chat.set_description(desc)
        await message.reply_text("✅ Group Description ကို ပြောင်းလဲလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# 🎨 FUN & BANNER
@app.on_message(filters.command("wimage"))
async def wimage_cmd(client: Client, message: Message):
    text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "Welcome To Our Group"
    encoded_text = text.replace(" ", "%20")
    img_url = f"https://image.pollinations.ai/prompt/welcome%20banner%20with%20text%20{encoded_text}%20glowing%20neon%20style"
    await message.reply_photo(photo=img_url, caption=f"✨ **Welcome Banner:** {text}")

@app.on_message(filters.command("couples"))
async def couples_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        return
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            members.append(member.user)
    if len(members) < 2:
        await message.reply_text("Group ထဲမှာ မန်ဘာ မလုံလောက်သေးပါဗျာ။")
        return
    c1, c2 = random.sample(members, 2)
    text = f"👩‍❤️‍👨 **ဒီနေ့အတွက် Group ရဲ့ စူပါ စုံတွဲ မဲပေါက်သူများ:**\n\n1️⃣ [{c1.first_name}](tg://user?id={c1.id})\n2️⃣ [{c2.first_name}](tg://user?id={c2.id})\n\n🎉 **Congratulations!**"
    await message.reply_text(text)

@app.on_message(filters.command("slap"))
async def slap_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 စနောက်ချင်သော မန်ဘာ၏ စာကို Reply ပြန်ပါ။")
        return
    sender = message.from_user.first_name
    target = message.reply_to_message.from_user.first_name
    slap_texts = [
        f"👋 **{sender}** က **{target}** ကို ပါးစပ်ပိတ်သွားအောင် ပါးရိုက်လိုက်ပါပြီ!",
        f"👋 **{sender}** က **{target}** ကို ငါးခြောက်နဲ့ ပါးလွှဲရိုက်လိုက်ပါတယ်!"
    ]
    await message.reply_text(random.choice(slap_texts))

# 🛠️ BASIC ADMIN COMMAND HANDLERS
@app.on_message(filters.command("ban"))
async def ban_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Ban ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.ban_member(user_id)
        await message.reply_text(f"⛔️ User `{user_id}` ကို Group မှ Ban လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("unban"))
async def unban_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply_text("💡 အသုံးပြုပုံ: `/unban 12345678` (User ID ထည့်ပေးပါ)")
        return
    try:
        user_id = int(args[1])
        await message.chat.unban_member(user_id)
        await message.reply_text(f"✅ User `{user_id}` အား Ban ဖြုတ်ပေးလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("mute"))
async def mute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Mute လုပ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.restrict_member(user_id, ChatPermissions())
        await message.reply_text(f"🔇 User `{user_id}` ၏ စာရိုက်ခွင့်ကို ပိတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("unmute"))
async def unmute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Unmute လုပ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.restrict_member(
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply_text(f"🔊 User `{user_id}` အား စာပြန်ရိုက်ခွင့် ပေးလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("kick"))
async def kick_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Group မှ ထုတ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.ban_member(user_id)
        await message.chat.unban_member(user_id)
        await message.reply_text(f"👞 User `{user_id}` ကို Group မှ ထုတ်ပစ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("gen"))
async def gen_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/gen a cat wearing sunglasses`")
        return
    prompt = message.text.split(maxsplit=1)[1]
    msg = await message.reply_text("🎨 AI မှ ပုံဖန်တီးပေးနေပါသည်...")
    try:
        encoded_prompt = prompt.replace(" ", "%20")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        await message.reply_photo(photo=image_url, caption=f"✨ **Prompt:** `{prompt}`")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

# 🎲 GAMES HANDLERS
@app.on_message(filters.command("dice"))
async def dice_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎲")

@app.on_message(filters.command("dart"))
async def dart_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎯")

@app.on_message(filters.command("basket"))
async def basket_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🏀")

@app.on_message(filters.command("bowling"))
async def bowling_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎳")

@app.on_message(filters.command("football"))
async def football_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="⚽")

@app.on_message(filters.command("slot"))
async def slot_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎰")

# 🎈 UTILITIES
@app.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start_time = time.time()
    msg = await message.reply_text("🏓 Pong!")
    end_time = time.time()
    ms = round((end_time - start_time) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⚡️ Speed: `{ms} ms`")

@app.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        await message.reply_text(f"👤 **Name:** {target.first_name}\n🆔 **User ID:** `{target.id}`")
    else:
        await message.reply_text(f"💬 **Group ID:** `{message.chat.id}`\n👤 **Your ID:** `{message.from_user.id}`")

@app.on_message(filters.command("broadcast"))
async def broadcast_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/broadcast သတင်းလွှာ စာသား`")
        return
    msg_to_send = message.text.split(maxsplit=1)[1]
    count = 0
    await message.reply_text("📢 Group အားလုံးသို့ ကြေညာစာများ ပို့ဆောင်နေပါသည်...")
    for chat_id in list(KNOWN_CHATS):
        try:
            await client.send_message(chat_id, f"📢 **ကြေညာချက်:**\n\n{msg_to_send}")
            count += 1
            await asyncio.sleep(0.5)
        except Exception:
            pass
    await message.reply_text(f"✅ စုစုပေါင်း Group/Chat **{count}** ခုသို့ ကြေညာစာ ပို့ပြီးပါပြီ။")

@app.on_message(filters.command("botstats"))
async def botstats_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    total_groups = len(KNOWN_CHATS)
    memory_count = 0
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            memory_count = len(f.readlines())
    stats_msg = (
        f"📊 **Bot ၏ အချက်အလက်စာရင်း**\n\n"
        f"🌐 **အသုံးပြုထားသော Group/Chat စုစုပေါင်း:** `{total_groups}` ခု\n"
        f"🧠 **မှတ်ထားသော စကားလုံး/စာကြောင်းပေါင်း:** `{memory_count}` ကြောင်း"
    )
    await message.reply_text(stats_msg)

@app.on_message(filters.command("add"))
async def add_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/add မင်္ဂလာပါဗျာ`")
        return
    text_to_add = message.text.split(maxsplit=1)[1]
    save_text(text_to_add)
    await message.reply_text(f"✅ စကားလုံး မှတ်ယူလိုက်ပါပြီ: \"{text_to_add}\"")

@app.on_message(filters.command("setchance"))
async def setchance_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply_text("💡 အသုံးပြုပုံ: `/setchance 50` (0 မှ 100 အထိ)")
        return
    chance = int(args[1])
    if 0 <= chance <= 100:
        CHAT_SETTINGS.setdefault(message.chat.id, {})["chance"] = chance
        await message.reply_text(f"🎯 Bot အလိုအလျောက် ဝင်ပြောမည့် နှုန်းကို {chance}% သို့ ပြောင်းလိုက်ပါပြီ။")

@app.on_message(filters.command("clearmemory"))
async def clearmemory_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        await message.reply_text("🗑️ မှတ်ထားသော စကားလုံး အားလုံးကို ရှင်းထုတ်ပြီးပါပြီ။")
    else:
        await message.reply_text("မှတ်တမ်းဖိုင် မရှိသေးပါဗျာ။")

@app.on_message(filters.command("pin"))
async def pin_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Pin ချင်တဲ့ စာကို Reply ပြန်ပြီး `/pin` လို့ ရိုက်ပါ။")
        return
    try:
        await message.reply_to_message.pin()
        await message.reply_text("📌 စာကို Pin လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("unpin"))
async def unpin_cmd(client: Client, message: Message):
    try:
        await client.unpin_chat_message(message.chat.id)
        await message.reply_text("📌 Pin ထားသည်ကို ပြန်ဖြုတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("del"))
async def del_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 ဖျက်ချင်သည့် စာကို Reply ပြန်ပြီး `/del` လို့ ရိုက်ပါ။")
        return
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("groupinfo"))
async def groupinfo_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command က Group ထဲမှာပဲ သုံးလို့ရပါတယ်။")
        return
    chat = message.chat
    info = (
        f"🏰 **Group အချက်အလက်**\n\n"
        f"• **အမည်:** {chat.title}\n"
        f"• **Group ID:** `{chat.id}`\n"
        f"• **Type:** {chat.type.value.capitalize()}\n"
        f"• **Members Count:** {await client.get_chat_members_count(chat.id)}"
    )
    await message.reply_text(info)

# 🔔 NEW MEMBER WELCOME LISTENER
@app.on_message(filters.new_chat_members)
async def welcome_listener(client: Client, message: Message):
    settings = CHAT_SETTINGS.get(message.chat.id, {})
    if settings.get("welcome", True):
        for member in message.new_chat_members:
            wel_text = f"👋 **မင်္ဂလာပါ [{member.first_name}](tg://user?id={member.id})!**\n\n{message.chat.title} Group မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။ ✨"
            await message.reply_text(wel_text)

# ⭐️ AUTO CHAT, LOCKS & ANTI-LINK LISTENER
ALL_COMMANDS = [
    "start", "help", "ping", "id", "tagall", "broadcast", "botstats", 
    "add", "setchance", "clearmemory", "pin", "unpin", "del", "groupinfo",
    "ban", "unban", "mute", "unmute", "kick", "gen", "tmute", "tban",
    "purge", "zombies", "cleanzombies", "admin", "admins", "antilink", "welcome",
    "settitle", "setgtitle", "setgdesc", "wimage", "couples", "slap",
    "dice", "dart", "basket", "bowling", "football", "cancel", "stop",
    "lock", "unlock", "warn", "unwarn", "warns", "userinfo", "info",
    "roll", "truth", "dare", "choose", "say", "nightmode", "math",
    "crypto", "time", "carbon", "slot", "adminlist", "dkick", "unpinall", "leavechat"
]

@app.on_message(~filters.command(ALL_COMMANDS))
async def handle_messages(client: Client, message: Message):
    if not message.chat:
        return

    KNOWN_CHATS.add(message.chat.id)

    me = await client.get_me()
    if message.from_user and message.from_user.id == me.id:
        return

    chat_settings = CHAT_SETTINGS.get(message.chat.id, {})

    # Check Locks
    if message.sticker and chat_settings.get("lock_sticker", False):
        await message.delete()
        return
    if message.photo and chat_settings.get("lock_photo", False):
        await message.delete()
        return
    if message.video and chat_settings.get("lock_video", False):
        await message.delete()
        return
    if message.audio and chat_settings.get("lock_audio", False):
        await message.delete()
        return
    if message.voice and chat_settings.get("lock_voice", False):
        await message.delete()
        return
    if message.document and chat_settings.get("lock_document", False):
        await message.delete()
        return
    if message.forward_date and chat_settings.get("lock_forward", False):
        await message.delete()
        return

    # Anti-Link Check
    if message.text:
        if chat_settings.get("antilink", False) or chat_settings.get("lock_link", False):
            if "http://" in message.text or "https://" in message.text or "t.me/" in message.text:
                try:
                    await message.delete()
                    warning = await message.reply_text(f"⚠️ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Group ထဲတွင် Link ပို့ခွင့်မပြုပါ။")
                    await asyncio.sleep(4)
                    await warning.delete()
                    return
                except Exception:
                    pass

        save_text(message.text)
        
        chat_id = message.chat.id
        auto_chance = chat_settings.get("chance", 100)

        if auto_chance > 0 and random.randint(1, 100) <= auto_chance:
            reply = generate_smart_reply(message.text)
            await message.reply_text(reply)

# 🚀 MAIN RUNNER
async def main():
    await start_web_server()
    print("Web Server စတင်ပါပြီ...")
    await app.start()
    print("Bot စတင်နေပါပြီ...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
