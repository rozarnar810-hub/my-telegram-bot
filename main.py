import os
import json
from difflib import get_close_matches
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# ==================== CONFIGURATION ====================
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = "8934169613:AAF1EdweBLj3ZRD5FA1SLJkIWu0s8sBQssE"
OWNER_ID = 7974865879

app = Client("flash_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

MEMORY_FILE = "chat_memory.json"

# ==================== CHAT MEMORY SYSTEM ====================
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

# ==================== BUTTON KEYBOARDS ====================
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
        ]
    ])

# ==================== COMMAND HANDLERS ====================
@app.on_message(filters.command(["start", "help"]))
async def help_command(client, message: Message):
    await message.reply_text(
        "🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**",
        reply_markup=main_menu_keyboard()
    )

# ==================== BUTTON CALLBACK HANDLER ====================
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 နောက်သို့", callback_data="main_menu")]])

    if data == "main_menu":
        await callback_query.message.edit_text(
            "🤖 **မင်္ဂလာပါဗျာ! အောက်ပါ Button လေးတွေကို နှိပ်ပြီး Commands များကို ကြည့်ရှုနိုင်ပါတယ်:**",
            reply_markup=main_menu_keyboard()
        )
    elif data == "owner_tools":
        if callback_query.from_user.id != OWNER_ID:
            await callback_query.answer("⚠️ ဒီမီနူးကို Bot Owner သာ သုံးခွင့်ရှိပါတယ်!", show_alert=True)
            return
        await callback_query.message.edit_text(
            "👑 **ပိုင်ရှင်သုံး Commands များ:**\n\n"
            "• `/broadcast` - မန်ဘာများ/Group များသို့ စာလှမ်းပို့ရန်\n"
            "• `/restart` - Bot ကို ပြန်စတင်ရန်",
            reply_markup=back_button
        )
    elif data == "tag_mention":
        await callback_query.message.edit_text(
            "📢 **Tag & Mention Commands များ:**\n\n"
            "• `/all` [စာ] - Group မန်ဘာအားလုံးကို Tag ခေါ်ရန်\n"
            "• `/cancel` - Tag ခေါ်နေတာကို ရပ်တန့်ရန်",
            reply_markup=back_button
        )
    elif data == "admin_tools":
        await callback_query.message.edit_text(
            "🛠️ **Admin Commands များ:**\n\n"
            "• `/ban` - မန်ဘာကို Ban ရန်\n"
            "• `/unban` - Ban ဖြုတ်ရန်\n"
            "• `/mute` - မန်ဘာ စာရေးခွင့် ပိတ်ရန်\n"
            "• `/unmute` - စာရေးခွင့် ပြန်ဖွင့်ရန်\n"
            "• `/pin` - စာကို Pin ချိတ်ရန်",
            reply_markup=back_button
        )
    elif data == "group_sec":
        await callback_query.message.edit_text(
            "🛡️ **Group လုံခြုံရေး:**\n\n"
            "• Spambot နဲ့ Link များ ပို့ပါက အလိုအလျောက် တားဆီးပေးမည်။",
            reply_markup=back_button
        )
    elif data == "cleaner":
        await callback_query.message.edit_text(
            "🧹 **Cleaner Commands:**\n\n"
            "• `/purge` - စာအများအပြား ဖျက်ရန်\n"
            "• `/del` - Reply ပြန်ထားသော စာကို ဖျက်ရန်",
            reply_markup=back_button
        )
    elif data == "ai_media":
        await callback_query.message.edit_text(
            "🎨 **AI & မီဒီယာ:**\n\n"
            "• စကားပြောပါက AI ဖြင့် မေးခွန်းများကို အလိုအလျောက် ပြန်လည်ဖြေကြားပေးပါမည်။",
            reply_markup=back_button
        )
    elif data == "fun_games":
        await callback_query.message.edit_text(
            "🎲 **ပျော်စရာဂိမ်းများ:**\n\n"
            "• `/dice` - အန်စာတုံး ပစ်ရန်\n"
            "• `/dart` - မြားပစ်ရန်",
            reply_markup=back_button
        )
    elif data == "general":
        await callback_query.message.edit_text(
            "🎈 **အထွေထွေ Commands:**\n\n"
            "• `/id` - မိမိ သို့မဟုတ် Group ID ကြည့်ရန်\n"
            "• `/info` - အကောင့် အချက်အလက် ကြည့်ရန်",
            reply_markup=back_button
        )
    elif data == "about":
        await callback_query.message.edit_text(
            "ℹ️ **ဘော့အကြောင်း:**\n\n"
            "• Flash Bot - Group Management & AI Assistant Bot ဖြစ်ပါတယ်။",
            reply_markup=back_button
        )
    elif data == "rules":
        await callback_query.message.edit_text(
            "📜 **စည်းကမ်းချက်များ:**\n\n"
            "• Group အတွင်း တခြားသူများကို ထိခိုက်စေသော စာများ၊ Link များ ပို့ခွင့်မရှိပါ။",
            reply_markup=back_button
        )

# ==================== AUTO LEARNING & SMART REPLY ====================
@app.on_message(filters.group & filters.text & ~filters.bot)
async def auto_learn_and_reply(client, message: Message):
    text = message.text.strip().lower()
    
    if text.startswith("/"):
        return

    # Member များ စကားပြော/Reply ပြန်တာကို မှတ်သားမည်
    if message.reply_to_message and message.reply_to_message.text:
        parent_text = message.reply_to_message.text.strip().lower()
        if not parent_text.startswith("/"):
            chat_db[parent_text] = message.text
            save_memory(chat_db)

    # မှတ်ထားသည့်ထဲမှ အနီးစပ်ဆုံး တူသည်များကို ပြန်ဖြေပေးမည်
    matches = get_close_matches(text, chat_db.keys(), n=1, cutoff=0.6)
    if matches:
        matched_key = matches[0]
        reply_text = chat_db[matched_key]
        await message.reply_text(reply_text)

if __name__ == "__main__":
    app.run()
