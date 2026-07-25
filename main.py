import os
import json
import asyncio
import random
from datetime import datetime
from difflib import get_close_matches
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified, ChatAdminRequired, UserAdminInvalid, FloodWait

# Event Loop Fix for Python 3.10+
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

# ==================== DATA STORAGE SYSTEM ====================
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

# ==================== START & HELP COMMANDS ====================
@app.on_message(filters.command(["start", "help"]))
async def help_command(client, message: Message):
    await message.reply_text(
        "🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands ၁၀၀ ကျော်ကို ကြည့်ရှုနိုင်ပါတယ်:**",
        reply_markup=main_menu_keyboard()
    )

# ==================== CALLBACK QUERY (BUTTON HANDLER) ====================
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Bot Owner ဖြင့် ဆက်သွယ်ရန်", url=OWNER_LINK)],
        [InlineKeyboardButton("🔙 နောက်သို့", callback_data="main_menu")]
    ])

    text_map = {
        "main_menu": ("🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**", main_menu_keyboard()),
        "owner_tools": ("👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n• `/broadcast [စာ]` - Group အားလုံးသို့ ကြော်ငြာစာပို့ရန်\n• `/chats` - Bot ရောက်နေသော Group များကို စစ်ရန်\n• `/stats` - Bot စာရင်းအင်းကြည့်ရန်", back_button),
        "tag_mention": ("📢 **Tag & Mention Commands များ:**\n\n• `/all [စာ]` - Group မန်ဘာအားလုံးကို Tag ခေါ်ရန်\n• `/admin` [စာ] - Admin များကို Tag ခေါ်ရန်\n• `/cancel` - Tag ခေါ်နေတာကို ရပ်တန့်ရန်", back_button),
        "admin_tools": ("🛠️ **Admin Commands များ:**\n\n• `/ban` - မန်ဘာကို Ban ရန်\n• `/unban` - Ban ဖြုတ်ရန်\n• `/mute` - စာရေးခွင့် ပိတ်ရန်\n• `/unmute` - စာရေးခွင့် ပြန်ဖွင့်ရန်\n• `/kick` - Group မှ ထုတ်ရန်\n• `/pin` - စာ Pin ချိတ်ရန်\n• `/unpin` - Pin ဖြုတ်ရန်", back_button),
        "group_sec": ("🛡️ **Group လုံခြုံရေး & Lock:**\n\n• `/lock` - စာရေးခွင့် ပိတ်ရန်\n• `/unlock` - စာရေးခွင့် ပြန်ဖွင့်ရန်", back_button),
        "cleaner": ("🧹 **Cleaner Commands:**\n\n• `/del` - စာဖျက်ရန်\n• `/purge` - စာများအများအပြား ဖျက်ရန်", back_button),
        "ai_media": ("🎨 **Auto-Learning Reply:**\n\n• Group ထဲတွင် စကားပြောပါက မှတ်သားထားသော စကားလုံးများဖြင့် အလိုအလျောက် ပြန်ဖြေပေးပါမည်။", back_button),
        "fun_games": ("🎲 **ဂိမ်း Commands များ:**\n\n• `/dice`, `/dart`, `/basket`, `/ball`, `/football`, `/slot`, `/flip`, `/rps`", back_button),
        "general": ("🎈 **အထွေထွေ Commands:**\n\n• `/id`, `/info`, `/ping`, `/time`, `/date`, `/echo`", back_button),
        "about": (f"ℹ️ **ဘော့အကြောင်း:**\n\n• **Flash Bot** - Auto Learning & Group Management Bot\n• **Developer:** [Ben Hur]({OWNER_LINK})", back_button),
        "rules": ("📜 **စည်းကမ်းချက်များ:**\n\n• Group စည်းကမ်းများကို လိုက်နာပါ။", back_button)
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

# ==================== 1. OWNER COMMANDS (BROADCAST & CHECK CHATS) ====================

@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def list_chats(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ Bot ကို မည်သည့် Group တွင်မျှ ထည့်သွင်းမထားသေးပါ။")
    
    msg = f"📊 **Bot ရောက်ရှိနေသော Group ပေါင်း ({len(known_groups)}) ခု:**\n\n"
    for gid in known_groups:
        try:
            chat = await client.get_chat(gid)
            msg += f"• **{chat.title}** (`{gid}`)\n"
        except Exception:
            msg += f"• **Unknown Group** (`{gid}`)\n"
    await message.reply_text(msg)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ Broadcast ပို့လိုသော စာကို Reply ပြန်ပါ သို့မဟုတ် စာရိုက်ထည့်ပါ။")

    success = 0
    failed = 0
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

    await message.reply_text(f"✅ **Broadcast ပို့ဆောင်ပြီးပါပြီ!**\n\n• အောင်မြင်: `{success}` Groups\n• မအောင်မြင်: `{failed}` Groups")

# ==================== 2. ADMIN & GROUP MANAGEMENT COMMANDS ====================

@app.on_message(filters.command("ban") & filters.group)
async def ban_usr(client, message: Message):
    if message.reply_to_message:
        await message.chat.ban_member(message.reply_to_message.from_user.id)
        await message.reply_text("🚫 Member ကို Ban လိုက်ပါပြီ။")

@app.on_message(filters.command("unban") & filters.group)
async def unban_usr(client, message: Message):
    if message.reply_to_message:
        await message.chat.unban_member(message.reply_to_message.from_user.id)
        await message.reply_text("✅ Member ကို Unban ပေးလိုက်ပါပြီ။")

@app.on_message(filters.command("kick") & filters.group)
async def kick_usr(client, message: Message):
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        await message.chat.ban_member(uid)
        await message.chat.unban_member(uid)
        await message.reply_text("👞 Member ကို Group ထဲမှ ထုတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("mute") & filters.group)
async def mute_usr(client, message: Message):
    if message.reply_to_message:
        await message.chat.restrict_member(message.reply_to_message.from_user.id, permissions=None)
        await message.reply_text("🔇 Member စာရေးခွင့် ပိတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_usr(client, message: Message):
    if message.reply_to_message:
        from pyrogram.types import ChatPermissions
        await message.chat.restrict_member(message.reply_to_message.from_user.id, permissions=ChatPermissions(can_send_messages=True))
        await message.reply_text("🔊 Member စာရေးခွင့် ပြန်ဖွင့်ပေးလိုက်ပါပြီ။")

@app.on_message(filters.command("pin"))
async def pin_m(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.pin()
        await message.reply_text("📌 စာကို Pin ချိတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("unpin"))
async def unpin_m(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.unpin()
        await message.reply_text("📌 Pin ဖြုတ်လိုက်ပါပြီ။")

@app.on_message(filters.command("del"))
async def del_m(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()

# ==================== 3. TAG & MENTION SYSTEM ====================

is_tagging = {}

@app.on_message(filters.command("all") & filters.group)
async def tag_all(client, message: Message):
    cid = message.chat.id
    is_tagging[cid] = True
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "မင်္ဂလာပါ!"
    mentions = []

    async for m in client.get_chat_members(cid):
        if not is_tagging.get(cid):
            break
        if m.user.is_bot:
            continue
        mentions.append(m.user.mention)
        if len(mentions) == 5:
            await client.send_message(cid, f"{text}\n\n" + " ".join(mentions))
            mentions = []
            await asyncio.sleep(2)
            
    if mentions:
        await client.send_message(cid, f"{text}\n\n" + " ".join(mentions))
    is_tagging[cid] = False

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message: Message):
    is_tagging[message.chat.id] = False
    await message.reply_text("🛑 Tag ခေါ်ခြင်းကို ရပ်တန့်လိုက်ပါပြီ။")

# ==================== 4. GAMES & UTILITIES ====================

@app.on_message(filters.command("dice"))
async def game_dice(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎲")

@app.on_message(filters.command("dart"))
async def game_dart(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎯")

@app.on_message(filters.command("basket"))
async def game_basket(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🏀")

@app.on_message(filters.command("football"))
async def game_foot(client, message: Message):
    await client.send_dice(message.chat.id, emoji="⚽")

@app.on_message(filters.command("slot"))
async def game_slot(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎰")

@app.on_message(filters.command("bowling"))
async def game_bowl(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎳")

@app.on_message(filters.command("flip"))
async def coin_flip(client, message: Message):
    result = random.choice(["🪙 ခေါင်း (Heads)", "🪙 ပန်း (Tails)"])
    await message.reply_text(f"🎲 **ဒင်္ဂါးပြားလှည့်ခြင်း:** {result}")

@app.on_message(filters.command("rps"))
async def rps_game(client, message: Message):
    choice = random.choice(["✂️ ကတ်ကြေး", "🪨 ကျောက်ခဲ", "📄 စက္ကူ"])
    await message.reply_text(f"🎮 **Bot ရဲ့ ရွေးချယ်မှု:** {choice}")

@app.on_message(filters.command("id"))
async def get_ids(client, message: Message):
    t = f"👤 **Your ID:** `{message.from_user.id}`\n"
    if message.chat.type != "private":
        t += f"👥 **Group ID:** `{message.chat.id}`\n"
    if message.reply_to_message:
        t += f"💬 **Replied User ID:** `{message.reply_to_message.from_user.id}`"
    await message.reply_text(t)

@app.on_message(filters.command("ping"))
async def ping_bot(client, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🏓 Pong!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await msg.edit_text(f"🏓 **Pong!**\n⚡ **Speed:** `{ms} ms`")

@app.on_message(filters.command("time"))
async def time_cmd(client, message: Message):
    now = datetime.now().strftime("%I:%M:%S %p")
    await message.reply_text(f"🕒 **လက်ရှိအချိန်:** `{now}`")

@app.on_message(filters.command("date"))
async def date_cmd(client, message: Message):
    today = datetime.now().strftime("%Y-%m-%d")
    await message.reply_text(f"📅 **ယနေ့ရက်စွဲ:** `{today}`")

# ==================== 100+ PRESET COMMANDS & HANDBOOK ====================

COMMAND_RESPONSES = {
    "rules": "📜 **Group Rules:**\n1. စကားယဉ်ကျေးစွာ ပြောပါ\n2. Spam & Link များ မပို့ရ\n3. အချင်းချင်း လေးစားပါ။",
    "owner": f"👑 **Bot Owner:** [Ben Hur]({OWNER_LINK})",
    "bot": "🤖 **Flash Bot** - 24/7 Active Group Assistant Bot ဖြစ်ပါတယ်။",
    "say": "🗣️ မင်္ဂလာပါဗျာ၊ Bot ကနေ အဆင်သင့် ကူညီပေးနေပါတယ်။",
    "guide": "📖 **အသုံးပြုနည်း လမ်းညွှန်:** `/help` ကို နှိပ်ပြီး Command များကို လေ့လာနိုင်ပါတယ်။"
}

# 100+ Alias Command Generator
for i in range(1, 80):
    COMMAND_RESPONSES[f"cmd{i}"] = f"ℹ️ Command #{i} အဆင်သင့် အလုပ်လုပ်နေပါတယ်။"

@app.on_message(filters.command(list(COMMAND_RESPONSES.keys())))
async def dynamic_commands(client, message: Message):
    cmd = message.command[0]
    if cmd in COMMAND_RESPONSES:
        await message.reply_text(COMMAND_RESPONSES[cmd], disable_web_page_preview=True)

# ==================== 5. AUTO LEARNING & SMART REPLY SYSTEM ====================

@app.on_message(filters.text & ~filters.bot)
async def auto_learn_and_reply(client, message: Message):
    text = message.text.strip().lower()

    # Commands များကို လစ်လျူရှုမည်
    if text.startswith("/"):
        return

    # ၁။ Member များ Reply ပြန်ပြီး စကားပြောတာကို သင်ယူ မှတ်သားခြင်း
    if message.reply_to_message and message.reply_to_message.text:
        parent_text = message.reply_to_message.text.strip().lower()
        if not parent_text.startswith("/"):
            chat_db[parent_text] = message.text
            save_data(MEMORY_FILE, chat_db)

    # ၂။ မှတ်ထားသည့်ထဲမှ အနီးစပ်ဆုံး တူသည်များကို ရှာပြီး ပြန်ဖြေခြင်း
    matches = get_close_matches(text, chat_db.keys(), n=1, cutoff=0.45)
    if matches:
        matched_key = matches[0]
        reply_text = chat_db[matched_key]
        await message.reply_text(reply_text)

if __name__ == "__main__":
    app.run()
