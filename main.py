import os
import asyncio
import random
import threading
import difflib
from http.server import HTTPServer, BaseHTTPRequestHandler
import markovify
from pyrogram import Client, filters
from pyrogram.types import Message

# Render Port Error မတက်အောင် Web Server ကို သီးသန့် Run ပေးခြင်း
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Active and Running")
        
    def log_message(self, format, *args):
        return  # Log တွေ ရှုပ်မနေအောင် ပိတ်ထားသည်

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Web Server ကို Background တွင် စတင်ခြင်း
threading.Thread(target=run_health_check_server, daemon=True).start()

# API Credentials
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 7974865879

DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}
KNOWN_CHATS = set()

app = Client("my_tag_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def save_text(text: str):
    if len(text.split()) >= 1 and not text.startswith("/"):
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")

def generate_smart_reply(user_message: str) -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲ၊ Group ထဲမှာ စကားများများ ပြောပေးကြပါ။"

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
        return "စကားပြန်ပြောဖို့ အချက်အလက် မရှိသေးပါဗျာ။"

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    KNOWN_CHATS.add(message.chat.id)
    await message.reply_text("မင်္ဂလာပါ။ AI Auto-Reply & Tag Bot ဖြစ်ပါတယ်။")

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🤖 **Bot အသုံးပြုနိုင်သော Command များ (Owner Only)**\n\n"
        "• `/tagall [စာသား]` - မန်ဘာ အားလုံးကို Tag ခေါ်ရန်\n"
        "• `/broadcast [စာသား]` - Group အားလုံးသို့ ကြေညာစာ ပို့ရန်\n"
        "• `/botstats` - Bot သုံးထားသော Group အရေအတွက် စစ်ရန်\n"
        "• `/add [စာသား]` - Bot ကို စကားသင်ပေးရန်\n"
        "• `/setchance [0-100]` - Auto ပြောမည့် နှုန်းသတ်မှတ်ရန်"
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("tagall"))
async def tagall_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command ကို Group ထဲမှာသာ အသုံးပြုနိုင်ပါတယ်ဗျာ။")
        return

    notice = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "လူစုံတက်စုံ သတိပေးချက်!"
    status_msg = await message.reply_text("🔍 Group ထဲရှိ မန်ဘာ အားလုံးကို စစ်ဆေးနေပါသည်...")

    try:
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)

        total_count = len(members)
        await status_msg.edit_text(f"📣 **{notice}**\n\n👥 စုစုပေါင်း မန်ဘာ **{total_count}** ယောက်အား Tag ခေါ်နေပါပြီ...")

        chunk_size = 5
        for i in range(0, total_count, chunk_size):
            chunk = members[i:i + chunk_size]
            mention_text = ""
            for user in chunk:
                name = user.first_name if user.first_name else "User"
                mention_text += f"[{name}](tg://user?id={user.id})  "

            await client.send_message(message.chat.id, mention_text)
            await asyncio.sleep(1.5)

    except Exception as e:
        await message.reply_text(f"❌ အမှားဖြစ်ပေါ်ပါသည်: {e}")

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
        await message.reply_text("💡 အသုံးပြုပုံ: `/setchance 20` (0 မှ 100 အထိ)")
        return

    chance = int(args[1])
    if 0 <= chance <= 100:
        CHAT_SETTINGS.setdefault(message.chat.id, {})["chance"] = chance
        await message.reply_text(f"🎯 Bot အလိုအလျောက် ဝင်ပြောမည့် နှုန်းကို {chance}% သို့ ပြောင်းလိုက်ပါပြီ။")

@app.on_message(filters.text & ~filters.command(["start", "help", "tagall", "broadcast", "botstats", "add", "setchance"]))
async def handle_messages(client: Client, message: Message):
    KNOWN_CHATS.add(message.chat.id)

    if message.chat.type.value == "private":
        reply = generate_smart_reply(message.text)
        await message.reply_text(reply)
        return

    save_text(message.text)
    chat_id = message.chat.id
    settings = CHAT_SETTINGS.get(chat_id, {"enabled": True, "chance": 0})
    
    if not settings.get("enabled", True):
        return

    bot = await client.get_me()
    is_mentioned = bot.username and f"@{bot.username}" in message.text
    is_reply = message.reply_to_message and message.reply_to_message.from_user.id == bot.id
    
    auto_chance = settings.get("chance", 0)
    should_reply = random.randint(1, 100) <= auto_chance if auto_chance > 0 else False

    if is_mentioned or is_reply or should_reply:
        reply = generate_smart_reply(message.text)
        await message.reply_text(reply)

print("Bot စတင်နေပါပြီ...")
app.run()
