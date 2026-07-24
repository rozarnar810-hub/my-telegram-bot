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
CHATS_FILE = "known_chats.txt"
CHAT_SETTINGS = {}
USER_WARNS = {}
AFK_USERS = {}  # {user_id: reason}
BANNED_WORDS = ["spamlink", "badword1", "badword2"] # လိုအပ်သော bad word များ ထည့်နိုင်သည်

# Global Control Flags
TAGGING_ACTIVE = {}

# Persistent Known Chats
def load_known_chats():
    chats = set()
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lstrip("-").isdigit():
                    chats.add(int(line.strip()))
    return chats

def save_known_chat(chat_id):
    KNOWN_CHATS.add(chat_id)
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        for c in KNOWN_CHATS:
            f.write(f"{c}\n")

KNOWN_CHATS = load_known_chats()

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

# 🔘 INTERACTIVE BUTTON UI
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
        ],
        [
            InlineKeyboardButton("ℹ️ About & Support", callback_data="help_about"),
            InlineKeyboardButton("📜 Rules & Policy", callback_data="help_rules")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 မူလ Help Menu သို့ ပြန်သွားရန်", callback_data="help_main")]])

# 🤖 BOT MAIN COMMANDS
@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    save_known_chat(message.chat.id)
    text = (
        "👋 **မင်္ဂလာပါ!**\n\n"
        "ကျွန်တော်ကတော့ Group မန်နေးဂျာ စနစ်၊ Admin တဂ်ခေါ်စနစ်၊ AI Auto-Chat၊ Security၊ AFK နဲ့ Fun Games များ အစုံအလင် ပါဝင်တဲ့ **24/7 Multi-Functional Telegram Bot** ဖြစ်ပါတယ်။\n\n"
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
            "• `/setrules [စာသား]` - Group စည်းကမ်းချက် သတ်မှတ်ရန်\n"
            "• `/rules` - Group စည်းကမ်းချက်များ ကြည့်ရန်\n"
            "• `/lock [type]` - Media ပိတ်ရန်\n"
            "• `/unlock [type]` - ပိတ်ထားသော Media ပြန်ဖွင့်ရန်\n"
            "• `/warn` / `/unwarn` / `/warns` - Warning စနစ် အသုံးပြုရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_admin":
        text = (
            "🛠️ **Admin & Moderation Tools**\n\n"
            "• `/ban` / `/unban [ID]` - Ban/Unban ပြုလုပ်ရန်\n"
            "• `/tban [10m/1h]` - အချိန်သတ်မှတ်၍ Ban ထားရန်\n"
            "• `/mute` / `/unmute` - စာရိုက်ခွင့် ပိတ်/ဖွင့် ရန်\n"
            "• `/tmute [10m/1h]` - အချိန်သတ်မှတ်၍ Mute ထားရန်\n"
            "• `/kick` / `/dkick` - Group မှ ထုတ်ရန်\n"
            "• `/pin` / `/unpin` / `/unpinall` - Pin/Unpin ပြုလုပ်ရန်\n"
            "• `/settitle [အမည်]` - Admin Title ပြောင်းရန်\n"
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
            "• `/nightmode [on/off]` - ညဘက် Group စာရိုက်ခွင့် ပိတ်/ဖွင့် ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_ai_media":
        text = (
            "🎨 **AI & Media Tools**\n\n"
            "• `/gen [Prompt]` - AI ဖြင့် ပုံဆွဲရန်\n"
            "• `/wimage [Text]` - Welcome Banner ပုံ ဖန်တီးရန်\n"
            "• `/carbon [Text]` - စာများကို Code Style Image ပြောင်းရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_games":
        text = (
            "🎲 **Fun & Games Commands**\n\n"
            "• `/couples` - Group စူပါစုံတွဲ မဲနှိုက်ရန် 👩‍❤️‍👨\n"
            "• `/slap` - မန်ဘာကို ပါးရိုက်ရန် 👋\n"
            "• `/roll` - ဂဏန်း Random နှိုက်ရန် (0-100)\n"
            "• `/truth` / `/dare` - Truth or Dare မေးခွန်းများ\n"
            "• `/choose [a] [b]` - Bot ကို ရွေးချယ်ခိုင်းရန်\n"
            "• `/dice` 🎲 / `/dart` 🎯 / `/basket` 🏀 / `/slot` 🎰"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_general":
        text = (
            "🎈 **General & Utility Commands**\n\n"
            "• `/afk [အကြောင်းအရာ]` - AFK Mode ဝင်ထားရန်\n"
            "• `/ping` - Bot မြန်ဆန်မှု (Speed) စစ်ရန်\n"
            "• `/id` - User သို့မဟုတ် Group ID ကြည့်ရန်\n"
            "• `/userinfo` / `/info` - User Profile စစ်ရန်\n"
            "• `/groupinfo` - Group အချက်အလက် ကြည့်ရန်\n"
            "• `/math [ပုစ္ဆာ]` - သင်္ချာ တွက်ချက်ရန်\n"
            "• `/time` - လက်ရှိ အချိန်နှင့် ရက်စွဲ ကြည့်ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_about":
        text = (
            "ℹ️ **Bot Information & Support**\n\n"
            "• **Developer:** Python Pyrogram-based AI Engine\n"
            "• **Version:** v3.0 Ultimate Edition\n"
            "• **Uptime:** 24/7 Online Server Status Active\n\n"
            "အကူအညီနှင့် မေးမြန်းလိုပါက Owner ထံ ဆက်သွယ်နိုင်ပါသည်။"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_rules":
        rules = CHAT_SETTINGS.get(query.message.chat.id, {}).get("rules", "ဤ Group တွင် သီးသန့် စည်းကမ်းချက် မသတ်မှတ်ရသေးပါ။")
        await query.message.edit_text(f"📜 **Group Rules & Policy:**\n\n{rules}", reply_markup=get_back_button())

# 💤 AFK SYSTEM
@app.on_message(filters.command("afk"))
async def afk_cmd(client: Client, message: Message):
    reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "မအားလပ်သေးပါ။"
    AFK_USERS[message.from_user.id] = reason
    await message.reply_text(f"💤 [{message.from_user.first_name}](tg://user?id={message.from_user.id}) သည် **AFK** သို့ ဝင်ရောက်လိုက်ပါပြီ။\n📝 အကြောင်းပြချက်: `{reason}`")

# 📜 RULES SETTING
@app.on_message(filters.command("setrules"))
async def setrules_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/setrules စည်းကမ်းချက်များ ရိုက်ထည့်ပါ`")
        return
    rules = message.text.split(maxsplit=1)[1]
    CHAT_SETTINGS.setdefault(message.chat.id, {})["rules"] = rules
    await message.reply_text("✅ Group စည်းကမ်းချက်များကို သတ်မှတ်ပြီးပါပြီ။")

@app.on_message(filters.command("rules"))
async def rules_cmd(client: Client, message: Message):
    rules = CHAT_SETTINGS.get(message.chat.id, {}).get("rules", "ဤ Group တွင် စည်းကမ်းချက်များ မသတ်မှတ်ရသေးပါဗျာ။")
    await message.reply_text(f"📜 **Group Rules:**\n\n{rules}")

# 📊 ACCURATE BOT STATS (FIXED)
@app.on_message(filters.command("botstats"))
async def botstats_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return
    
    save_known_chat(message.chat.id)
    total_groups = len(KNOWN_CHATS)
    memory_count = 0
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            memory_count = len([l for l in f.readlines() if l.strip()])
            
    stats_msg = (
        f"📊 **Bot ၏ အချက်အလက်စာရင်း**\n\n"
        f"🌐 **အသုံးပြုထားသော Group/Chat စုစုပေါင်း:** `{total_groups}` ခု\n"
        f"🧠 **မှတ်ထားသော စကားလုံး/စာကြောင်းပေါင်း:** `{memory_count}` ကြောင်း"
    )
    await message.reply_text(stats_msg)

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

# 🔒 LOCK & UNLOCK SYSTEM
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

# 🧮 UTILITIES & FUN HANDLERS
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
    questions = ["မင်းရဲ့ အကြီးမားဆုံး လျှို့ဝှက်ချက်က ဘာလဲ။", "Group ထဲမှာ ဘယ်သူ့ကို အချစ်ဆုံးလဲ။", "နောက်ဆုံး ငိုခဲ့ရတဲ့ အကြောင်းအရင်းက ဘာလဲ။"]
    await message.reply_text(f"🤔 **Truth:** {random.choice(questions)}")

@app.on_message(filters.command("dare"))
async def dare_cmd(client: Client, message: Message):
    dares = ["Group ထဲမှာ စတစ်ကာ ၅ ခု ဆက်တိုက် ပို့ပါ။", "မင်းရဲ့ အမိုက်ဆုံး ပုံတစ်ပုံ Group ထဲ ပို့ပါ။", "စော်/ဘဲ ဆီ 'ငါမင်းကို လွမ်းတယ်' လို့ စာသွားပို့ပါ။"]
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

# ⏱️ TIMED MODERATION & KICK
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
    await msg.edit_text(f"🧟 Group ထဲတွင် Deleted Accounts စုစုပေါင်း: **{deleted_count}** ခု ရှိနေပါသည်။")

@app.on_message(filters.command("cleanzombies"))
async def cleanzombies_cmd(client: Client, message: Message):
    deleted_count = 0
    msg = await message.reply_text("🧹 Deleted Accounts များကို ထုတ်ပစ်နေပါသည်...")
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            try:
                await message.chat.ban_member(member.user.id)
                await message.chat.unban_member(member.user.id)
                deleted_count += 1
            except Exception:
                pass
    await msg.edit_text(f"✅ Deleted Accounts စုစုပေါင်း **{deleted_count}** ခုအား ထုတ်ပစ်ပြီးပါပြီ။")

# 👋 NEW MEMBER WELCOME HANDLER
@app.on_message(filters.new_chat_members)
async def welcome_handler(client: Client, message: Message):
    save_known_chat(message.chat.id)
    chat_id = message.chat.id
    if CHAT_SETTINGS.get(chat_id, {}).get("welcome", True):
        for member in message.new_chat_members:
            rules = CHAT_SETTINGS.get(chat_id, {}).get("rules", "စည်းကမ်းများ ဖတ်ရန် /rules ကို ရိုက်ပါ။")
            await message.reply_text(f"👋 **မင်္ဂလာပါ** [{member.first_name}](tg://user?id={member.id})!\n\n{message.chat.title} မှ လှိုက်လှဲစွာ ကြိုဆိုပါတယ်။ ✨\n\n📜 **Group Rules:** {rules}")

# 💬 SMART AUTO-CHAT & MEMORY LEARNING SYSTEM
@app.on_message(filters.text & ~filters.command(["start", "help", "botstats", "tagall", "cancel", "stop", "admin", "admins", "ban", "unban", "mute", "unmute", "del", "purge", "zombies", "cleanzombies", "antilink", "setchance", "add", "clearmemory", "broadcast", "say", "leavechat", "welcome", "rules", "setrules", "lock", "unlock", "warn", "unwarn", "warns", "nightmode", "dkick", "tmute", "tban", "math", "time", "carbon", "userinfo", "info", "adminlist", "roll", "truth", "dare", "choose", "afk"]))
async def smart_chat_handler(client: Client, message: Message):
    save_known_chat(message.chat.id)
    text = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # AFK Checker
    if message.reply_to_message and message.reply_to_message.from_user.id in AFK_USERS:
        replied_user = message.reply_to_message.from_user
        reason = AFK_USERS[replied_user.id]
        await message.reply_text(f"💤 [{replied_user.first_name}](tg://user?id={replied_user.id}) သည် **AFK** ဝင်နေပါသည်\n📝 အကြောင်းပြချက်: `{reason}`")
        
    if user_id in AFK_USERS:
        del AFK_USERS[user_id]
        await message.reply_text(f"👋 [{message.from_user.first_name}](tg://user?id={user_id}) **AFK** မှ ပြန်လည်ရောက်ရှိလာပါပြီ။")

    # Anti-Spam / Anti-Link Checking
    if CHAT_SETTINGS.get(chat_id, {}).get("antilink", False):
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                await message.delete()
                warning = await message.reply_text(f"⚠️ [{message.from_user.first_name}](tg://user?id={user_id}) Link ပို့ခွင့် ပိတ်ထားပါသည်။")
                await asyncio.sleep(4)
                await warning.delete()
                return
            except Exception:
                pass

    # Banned Words Check
    if any(b_word in text.lower() for b_word in BANNED_WORDS):
        try:
            await message.delete()
            return
        except Exception:
            pass

    save_text(text)

    is_mentioned = False
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == (await client.get_me()).id:
            is_mentioned = True

    bot_obj = await client.get_me()
    if bot_obj.username and f"@{bot_obj.username.lower()}" in text.lower():
        is_mentioned = True

    chance = CHAT_SETTINGS.get(chat_id, {}).get("chance", 30)

    if is_mentioned or (random.randint(1, 100) <= chance):
        await client.send_chat_action(chat_id, "typing")
        await asyncio.sleep(0.5)
        reply = generate_smart_reply(text)
        await message.reply_text(reply)

# 🏁 BOT STARTUP ENTRY POINT
async def main():
    await start_web_server()
    await app.start()
    print("🚀 Bot is Online & Web Server is Running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
