import asyncio

# Python 3.14+ Render Event Loop Fix (ဒါမှ မတက်တော့မှာပါ)
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import os
import sys
import time
import random
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# =========================================
# CONFIGURATION
# =========================================
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = "8934169613:AAF1EdweBLj3ZRD5FA1SLJkIWu0s8sBQssE"
OWNER_ID = 7974865879
PREFIX = ["/", "."]

app = Client(
    "flash_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

START_TIME = time.time()
LEARNING_ACTIVE = True
AUTO_REPLY_ACTIVE = True

# Database Setup
conn = sqlite3.connect("chat_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT UNIQUE)")
conn.commit()

# =========================================
# SMART CONTEXT-MATCHING AUTO-CHAT ENGINE
# =========================================
def get_best_matching_reply(user_text: str):
    try:
        cursor.execute("SELECT text FROM messages")
        all_msgs = [row[0] for row in cursor.fetchall()]
        
        if not all_msgs:
            return None

        user_words = [w.lower() for w in user_text.split() if len(w) > 1]
        
        if not user_words:
            return random.choice(all_msgs)

        max_matches = 0
        matched_candidates = []

        for db_text in all_msgs:
            db_words = [w.lower() for w in db_text.split()]
            common_words = set(user_words).intersection(set(db_words))
            match_count = len(common_words)
            
            if match_count > max_matches:
                max_matches = match_count
                matched_candidates = [db_text]
            elif match_count == max_matches and match_count > 0:
                matched_candidates.append(db_text)

        if matched_candidates and max_matches > 0:
            return random.choice(matched_candidates)
        
        return random.choice(all_msgs)
    except Exception:
        return None

@app.on_message(filters.group & ~filters.me & filters.text, group=1)
async def auto_chat_engine(client: Client, message: Message):
    global LEARNING_ACTIVE, AUTO_REPLY_ACTIVE
    text = message.text.strip()
    
    if LEARNING_ACTIVE and not any(text.startswith(p) for p in PREFIX) and len(text) > 1:
        try:
            cursor.execute("INSERT OR IGNORE INTO messages (text) VALUES (?)", (text,))
            conn.commit()
        except Exception:
            pass

    if AUTO_REPLY_ACTIVE and not any(text.startswith(p) for p in PREFIX):
        if random.random() < 0.8:
            reply_text = get_best_matching_reply(text)
            if reply_text:
                await asyncio.sleep(1)
                await message.reply_text(reply_text)

# =========================================
# INLINE BUTTONS MENU UI
# =========================================
def main_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 Owner Tools", callback_data="menu_owner"),
            InlineKeyboardButton("📢 Tag & Mention", callback_data="menu_tag")
        ],
        [
            InlineKeyboardButton("🛡 Group Security", callback_data="menu_sec"),
            InlineKeyboardButton("🛠 Admin Tools", callback_data="menu_admin")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner & Night", callback_data="menu_cleaner"),
            InlineKeyboardButton("🎨 AI & Media", callback_data="menu_ai")
        ],
        [
            InlineKeyboardButton("🎲 Fun & Games", callback_data="menu_fun"),
            InlineKeyboardButton("🎈 General & Utility", callback_data="menu_gen")
        ],
        [
            InlineKeyboardButton("ℹ️ About & Support", callback_data="menu_about"),
            InlineKeyboardButton("📜 Rules & Policy", callback_data="menu_rules")
        ]
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
    ])

# =========================================
# HELP MENU & CALLBACKS
# =========================================
@app.on_message(filters.command("help", prefixes=PREFIX))
async def help_command(client: Client, message: Message):
    await message.reply_text("🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**", reply_markup=main_help_keyboard())

@app.on_callback_query()
async def handle_callbacks(client: Client, callback: CallbackQuery):
    data = callback.data
    
    if data == "menu_main":
        await callback.message.edit_text("🤖 **Bot Help Menu - အမျိုးအစား ရွေးချယ်ပါ:**", reply_markup=main_help_keyboard())
    elif data == "menu_owner":
        await callback.message.edit_text("👑 **Owner Tools Commands:**\n\n• `/botchat` - Auto Chat On/Off\n• `/learn` - Auto Learn On/Off\n• `/clearmem` - Clear Memory\n• `/restart` - Restart Bot\n• `/gcast` - Broadcast Message", reply_markup=back_keyboard())
    elif data == "menu_tag":
        await callback.message.edit_text("📢 **Tag & Mention Commands:**\n\n• `/all <text>` - Mention all members\n• `/tagadmin` - Mention all admins\n• `/cancel` - Stop tagging", reply_markup=back_keyboard())
    elif data == "menu_sec":
        await callback.message.edit_text("🛡 **Group Security Commands:**\n\n• `/lock` - Lock Chat\n• `/unlock` - Unlock Chat\n• `/antispam` - Anti Spam Filter\n• `/nightmode` - Night Mode Settings", reply_markup=back_keyboard())
    elif data == "menu_admin":
        await callback.message.edit_text("🛠 **Admin Tools Commands:**\n\n• `/ban` - Ban User\n• `/unban` - Unban User\n• `/kick` - Kick User\n• `/mute` - Mute User\n• `/unmute` - Unmute User\n• `/pin` - Pin Message\n• `/purge` - Delete Messages", reply_markup=back_keyboard())
    elif data == "menu_cleaner":
        await callback.message.edit_text("🧹 **Cleaner & Night Commands:**\n\n• `/zombies` - Clean Deleted Accounts\n• `/del` - Delete Message\n• `/clean` - Clean Group Messages", reply_markup=back_keyboard())
    elif data == "menu_ai":
        await callback.message.edit_text("🎨 **AI & Media Commands:**\n\n• `/ai` - AI Chat Assistant\n• `/img` - Image Generator\n• `/song` - Download Audio\n• `/video` - Download Video", reply_markup=back_keyboard())
    elif data == "menu_fun":
        await callback.message.edit_text("🎲 **Fun & Games Commands:**\n\n• `/dice` - Roll Dice\n• `/dart` - Play Dart\n• `/basketball` - Play Basketball\n• `/shout` - Shout Text\n• `/type` - Type Animation", reply_markup=back_keyboard())
    elif data == "menu_gen":
        await callback.message.edit_text("🎈 **General & Utility Commands:**\n\n• `/ping` - Check Latency\n• `/id` - Get User/Chat ID\n• `/info` - User Information\n• `/calc` - Calculator", reply_markup=back_keyboard())
    elif data == "menu_about":
        await callback.message.edit_text(f"ℹ️ **About & Support:**\n\n• **Owner ID:** `{OWNER_ID}`\n• Flash Bot v2.0\n• Powered by Smart Matching Engine.", reply_markup=back_keyboard())
    elif data == "menu_rules":
        await callback.message.edit_text("📜 **Rules & Policy:**\n\n1. Spammings are restricted.\n2. Do not abuse system commands.", reply_markup=back_keyboard())

# =========================================
# BOT CONTROL COMMANDS
# =========================================
@app.on_message(filters.command("botchat", prefixes=PREFIX) & filters.user(OWNER_ID))
async def toggle_autochat(c, m):
    global AUTO_REPLY_ACTIVE; AUTO_REPLY_ACTIVE = not AUTO_REPLY_ACTIVE
    await m.reply_text(f"🤖 Auto Chat Engine: `{'ON 🟢' if AUTO_REPLY_ACTIVE else 'OFF 🔴'}`")

@app.on_message(filters.command("learn", prefixes=PREFIX) & filters.user(OWNER_ID))
async def toggle_learn(c, m):
    global LEARNING_ACTIVE; LEARNING_ACTIVE = not LEARNING_ACTIVE
    await m.reply_text(f"🧠 Auto-Learn: `{'ON 🟢' if LEARNING_ACTIVE else 'OFF 🔴'}`")

@app.on_message(filters.command("clearmem", prefixes=PREFIX) & filters.user(OWNER_ID))
async def clear_memory(c, m): 
    cursor.execute("DELETE FROM messages"); conn.commit(); await m.reply_text("🗑 DB Memory Cleared!")

@app.on_message(filters.command("ping", prefixes=PREFIX))
async def cmd_ping(c, m):
    start = time.time(); msg = await m.reply_text("`Pinging...`")
    await msg.edit_text(f"🏓 **Pong!** `{int((time.time() - start) * 1000)}ms`")

# =========================================
# START BOT
# =========================================
if __name__ == "__main__":
    app.run()
