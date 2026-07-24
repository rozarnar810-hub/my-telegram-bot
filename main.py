import asyncio
import json
import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TG_Bot")

# ==================== CONFIGURATION ====================
API_ID = 12345678  # သင့် API ID
API_HASH = "YOUR_API_HASH_HERE"  # သင့် API HASH
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # သင့် Bot Token

app = Client("tg_maybe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Global Storage Variables
ME_ID = None
TAGGING_CHATS = []
SERVED_CHATS = set()  # Group/Chat စာရင်းမှတ်ရန်

# ==================== 🧠 AUTO-LEARN CHATBOT DATABASE ====================
DB_FILE = "chatbot_db.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ==================== BOT STARTUP ====================
async def init_me():
    global ME_ID
    me = await app.get_me()
    ME_ID = me.id
    logger.info(f"[TG_Bot] Started as {me.first_name} ({ME_ID})")


# ==================== 🔘 INLINE BUTTON HELP MENU ====================


def help_main_menu():
    buttons = [
        [
            InlineKeyboardButton("👑 Owner Tools", callback_data="help_owner"),
            InlineKeyboardButton(
                "📢 Tag & Mention", callback_data="help_tag"
            ),
        ],
        [
            InlineKeyboardButton("🛡️ Group Security", callback_data="help_sec"),
            InlineKeyboardButton("🛠️ Admin Tools", callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton(
                "🧹 Cleaner & Night", callback_data="help_clean"
            ),
            InlineKeyboardButton("🎨 AI & Media", callback_data="help_ai"),
        ],
        [
            InlineKeyboardButton("🎲 Fun & Games", callback_data="help_fun"),
            InlineKeyboardButton(
                "📍 General & Utility", callback_data="help_gen"
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ About & Support", callback_data="help_about"
            ),
            InlineKeyboardButton(
                "📜 Rules & Policy", callback_data="help_rules"
            ),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        "🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**",
        reply_markup=help_main_menu(),
    )


@app.on_callback_query(filters.regex("^help_"))
async def help_callback(client: Client, query: CallbackQuery):
    data = query.data
    back_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 နောက်သို့", callback_data="help_back")]]
    )

    if data == "help_back":
        await query.message.edit_text(
            "🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**",
            reply_markup=help_main_menu(),
        )
    elif data == "help_tag":
        await query.message.edit_text(
            "📢 **Tag & Mention Commands:**\n\n"
            "• `/tag [စာသား]` - အဖွဲ့ဝင်များအားလုံးကို Tag ခေါ်ရန်\n"
            "• `/admin` - Admin များကိုသာ Tag ခေါ်ရန်\n"
            "• `/cancel` - Tag ခေါ်နေခြင်းကို ရပ်တန့်ရန်",
            reply_markup=back_button,
        )
    elif data == "help_gen":
        await query.message.edit_text(
            "📍 **General & Utility Commands:**\n\n"
            "• `/botstats` - Bot ၏ အချက်အလက် စာရင်းကြည့်ရန်\n"
            "• `/id` - Chat ID သို့မဟုတ် User ID ကြည့်ရန်\n"
            "• `/ping` - Bot အခြေအနေ စစ်ရန်",
            reply_markup=back_button,
        )
    else:
        await query.message.edit_text(
            f"🛠️ **{data.replace('help_', '').upper()} Commands:**\n\n"
            "ဤ ကဏ္ဍအတွက် Commands များ အလုပ်လုပ်နေပါသည်။",
            reply_markup=back_button,
        )


# ==================== 📊 BOT STATS COMMAND ====================


@app.on_message(filters.command("botstats"))
async def bot_stats(client: Client, message: Message):
    db = load_db()
    total_words = len(db)
    total_chats = len(SERVED_CHATS) if SERVED_CHATS else 1

    stats_text = (
        "📊 **Bot ၏ အချက်အလက်စာရင်း:**\n\n"
        f"🌐 **အသုံးပြုထားသော Group/Chat စုစုပေါင်း:** {total_chats} ခု\n"
        f"🧠 **မှတ်ထားသော စကားလုံး/စာကြောင်းပေါင်း:** {total_words} ကြောင်း"
    )
    await message.reply_text(stats_text)


# ==================== 💬 AUTO-LEARN CHATBOT SYSTEM ====================


# မန်ဘာများ ပြောသမျှ စကားလုံးများကို အလိုအလျောက် မှတ်သားပြီး ပြန်ပြောသည့် စနစ်
@app.on_message(filters.text & ~filters.me)
async def auto_learn_chatbot(client: Client, message: Message):
    if message.chat.id not in SERVED_CHATS:
        SERVED_CHATS.add(message.chat.id)

    if message.text.startswith("/"):
        return

    text = message.text.strip()
    db = load_db()

    # ၁။ Reply ပြန်ပြီး စကားသင်ပေးသည့် စနစ် (Auto-Learn)
    if message.reply_to_message and message.reply_to_message.text:
        question = message.reply_to_message.text.lower().strip()
        answer = text

        # မေးခွန်းနှင့် အဖြေကို အလိုအလျောက် Database ထဲ မှတ်သားခြင်း
        if question and answer and not question.startswith("/"):
            db[question] = answer
            save_db(db)

    # ၂။ မှတ်သားထားသော စကားလုံးပါပါက အလိုအလျောက် စကားပြန်ပြောခြင်း
    user_msg = text.lower()
    for q, a in db.items():
        if q in user_msg:
            try:
                # ChatAction.TYPING သေချာသုံးထားသဖြင့် AttributeError မတက်တော့ပါ
                await client.send_chat_action(
                    message.chat.id, ChatAction.TYPING
                )
                await asyncio.sleep(1)
                await message.reply_text(a)
                break
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                logger.error(f"Chatbot Reply Error: {e}")


# ==================== RUN BOT ====================
async def main():
    await app.start()
    await init_me()
    logger.info("🚀 TG_Bot is Running...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
