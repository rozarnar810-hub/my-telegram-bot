import os
import json
import asyncio
from difflib import get_close_matches
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified

# Asyncio Event Loop Fix for Python 3.10+
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

# ==================== CHAT MEMORY FUNCTIONS ====================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

chat_db = load_memory()

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
            InlineKeyboardButton("🧹 Cleaner & Night", callback_data="cleaner"),
            InlineKeyboardButton("🎨 AI & မီဒီယာ", callback_data="ai_media")
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

# ==================== START / HELP COMMAND ====================
@app.on_message(filters.command(["start", "help"]))
async def help_command(client, message: Message):
    await message.reply_text(
        "🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**",
        reply_markup=main_menu_keyboard()
    )

# ==================== CALLBACK QUERY (BUTTONS) ====================
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Bot Owner ဖြင့် ဆက်သွယ်ရန်", url=OWNER_LINK)],
        [InlineKeyboardButton("🔙 နောက်သို့", callback_data="main_menu")]
    ])

    text_map = {
        "main_menu": ("🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**", main_menu_keyboard()),
        "owner_tools": ("👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n• `/broadcast [စာ]` - မန်ဘာများ/Group များသို့ စာလှမ်းပို့ရန်", back_button),
        "tag_mention": ("📢 **Tag & Mention Commands များ:**\n\n• `/all [စာ]` - Group မန်ဘာအားလုံးကို Tag ခေါ်ရန်\n• `/cancel` - Tag ခေါ်နေတာကို ရပ်တန့်ရန်", back_button),
        "admin_tools": ("🛠️ **Admin Commands များ:**\n\n• `/ban` (Reply) - မန်ဘာကို Ban ရန်\n• `/unban` (Reply) - Ban ဖြုတ်ရန်\n• `/mute` (Reply) - စာရေးခွင့် ပိတ်ရန်\n• `/unmute` (Reply) - စာရေးခွင့် ပြန်ဖွင့်ရန်\n• `/pin` (Reply) - စာကို Pin ချိတ်ရန်", back_button),
        "group_sec": ("🛡️ **Group လုံခြုံရေး:**\n\n• Bot ကို Group ထဲ Admin ပေးထားပါက မလိုလားအပ်သော စပမ်များကို တားဆီးပေးပါမည်။", back_button),
        "cleaner": ("🧹 **Cleaner Commands:**\n\n• `/del` (Reply) - ပြန်ထားသော စာကို ဖျက်ရန်", back_button),
        "ai_media": ("🎨 **AI & မီဒီယာ:**\n\n• Group ထဲတွင် စကားပြောပါက မှတ်သားထားသော စကားလုံးများဖြင့် အလိုအလျောက် ပြန်ဖြေပေးပါမည်။", back_button),
        "fun_games": ("🎲 **ပျော်စရာဂိမ်းများ:**\n\n• `/dice` - အန်စာတုံး ပစ်ရန်\n• `/dart` - မြားပစ်ရန်", back_button),
        "general": ("🎈 **အထွေထွေ Commands:**\n\n• `/id` - မိမိ သို့မဟုတ် Group ID ကြည့်ရန်\n• `/info` - အကောင့် အချက်အလက် ကြည့်ရန်", back_button),
        "about": (f"ℹ️ **ဘော့အကြောင်း:**\n\n• **Flash Bot** - Group Management & Auto Learning Bot ဖြစ်ပါတယ်။\n• **Developer:** [Ben Hur]({OWNER_LINK})", back_button),
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

# ==================== WORKING COMMANDS ====================

# 1. ID Check Command
@app.on_message(filters.command("id"))
async def get_id(client, message: Message):
    text = f"👤 **Your ID:** `{message.from_user.id}`\n"
    if message.chat.type != "private":
        text += f"👥 **Group ID:** `{message.chat.id}`\n"
    if message.reply_to_message:
        text += f"💬 **Replied User ID:** `{message.reply_to_message.from_user.id}`"
    await message.reply_text(text)

# 2. Tag All Command
is_tagging = {}
@app.on_message(filters.command("all") & filters.group)
async def tag_all_members(client, message: Message):
    chat_id = message.chat.id
    is_tagging[chat_id] = True
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "မင်္ဂလာပါ!"
    usr_mentions = []
    
    async for member in client.get_chat_members(chat_id):
        if not is_tagging.get(chat_id):
            break
        if member.user.is_bot:
            continue
        usr_mentions.append(member.user.mention)
        if len(usr_mentions) == 5:
            await client.send_message(chat_id, f"{text}\n\n" + " ".join(usr_mentions))
            usr_mentions = []
            await asyncio.sleep(2)
            
    if usr_mentions:
        await client.send_message(chat_id, f"{text}\n\n" + " ".join(usr_mentions))
    is_tagging[chat_id] = False

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tagging(client, message: Message):
    is_tagging[message.chat.id] = False
    await message.reply_text("🛑 **Tag ခေါ်ယူခြင်းကို ရပ်တန့်လိုက်ပါပြီ။**")

# 3. Admin Tools
@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Ban ချင်သည့် မန်ဘာ၏ စာကို Reply ပြန်ပြီး သုံးပါ!")
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.ban_member(user_id)
        await message.reply_text(f"🚫 {message.reply_to_message.from_user.mention} ကို Ban လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Unban ချင်သည့် မန်ဘာ၏ စာကို Reply ပြန်ပြီး သုံးပါ!")
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.unban_member(user_id)
        await message.reply_text(f"✅ {message.reply_to_message.from_user.mention} ကို Unban ပေးလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")

@app.on_message(filters.command("del"))
async def delete_msg(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()

@app.on_message(filters.command("pin"))
async def pin_msg(client, message: Message):
    if message.reply_to_message:
        await message.reply_to_message.pin()
        await message.reply_text("📌 စာကို Pin ချိတ်လိုက်ပါပြီ။")

# 4. Games Command
@app.on_message(filters.command("dice"))
async def send_dice(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎲")

@app.on_message(filters.command("dart"))
async def send_dart(client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎯")

# ==================== AUTO LEARNING & SMART REPLY SYSTEM ====================
@app.on_message(filters.text & ~filters.bot)
async def auto_learn_and_reply(client, message: Message):
    text = message.text.strip().lower()
    
    # Command စာလုံးများဖြစ်ပါက ကျော်မည်
    if text.startswith("/"):
        return

    # ၁။ မန်ဘာများ စကားပြောတာကို သင်ယူခြင်း (Learn from replies)
    if message.reply_to_message and message.reply_to_message.text:
        parent_text = message.reply_to_message.text.strip().lower()
        if not parent_text.startswith("/"):
            chat_db[parent_text] = message.text
            save_memory(chat_db)

    # ၂။ မှတ်ထားသော စကားလုံးများနှင့် အနီးစပ်ဆုံး တူပါက အလိုအလျောက် ပြန်ဖြေခြင်း
    matches = get_close_matches(text, chat_db.keys(), n=1, cutoff=0.5)
    if matches:
        matched_key = matches[0]
        reply_text = chat_db[matched_key]
        await message.reply_text(reply_text)

if __name__ == "__main__":
    app.run()
