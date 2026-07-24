import os
import asyncio
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import markovify
from pyrogram import Client, filters
from pyrogram.types import Message

# Render မအိပ်စေရန် Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Active")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# 🔑 သင့် Screenshot ထဲမှ API credentials များ
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}

app = Client("my_tag_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def save_text(text: str):
    if len(text.split()) >= 1 and not text.startswith("/"):
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def generate_ai_reply() -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲ၊ Group ထဲမှာ စကားများများ ပြောပေးကြပါ။"
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            text_data = f.read()
        if len(text_data.strip()) == 0:
            return "စကားလုံး အချက်အလက် မရှိသေးပါဗျာ။"

        text_model = markovify.NewlineText(text_data, state_size=1)
        reply = text_model.make_sentence(tries=100)
        return reply if reply else random.choice(text_data.strip().split("\n"))
    except Exception:
        return "စကားပြန်ပြောဖို့ အချက်အလက် မရှိသေးပါဗျာ။"

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.value in ["owner", "administrator"]
    except Exception:
        return False

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text("မင်္ဂလာပါ။ Group Member အားလုံးကို အလိုအလျောက် စစ်ဆေးပြီး Tag ခေါ်ပေးနိုင်သော AI Bot ဖြစ်ပါတယ်ဗျာ။ /help ကို နှိပ်ပါ၊")

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🤖 **Bot အသုံးပြုနိုင်သော Command များ**\n\n"
        "📢 **Tag စနစ်:**\n"
        "• `/tagall [စာသား]` - Group ထဲရှိ မန်ဘာ အားလုံးကို အလိုအလျောက် စစ်ဆေးပြီး Mention ခေါ်ရန်\n\n"
        "💬 **AI & Group Management:**\n"
        "• `/setchance [0-100]` - Auto ပြောမည့် နှုန်းသတ်မှတ်ရန်\n"
        "• `/boton` / `/botoff` - Bot ပိတ်/ဖွင့်ရန်"
    )
    await message.reply_text(help_text)

# ⭐️ မန်ဘာ ဘယ်လောက်ရှိရှိ အရင် Auto စစ်ဆေးပြီး Tag ခေါ်ပေးသည့် စနစ်
@app.on_message(filters.command("tagall"))
async def tagall_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command ကို Group ထဲမှာသာ အသုံးပြုနိုင်ပါတယ်ဗျာ။")
        return

    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ Admin သာလျှင် Member များကို Tag ခေါ်နိုင်ပါတယ်။")
        return

    notice = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "လူစုံတက်စုံ သတိပေးချက်!"
    status_msg = await message.reply_text("🔍 Group ထဲရှိ မန်ဘာ အားလုံးကို စစ်ဆေးနေပါသည်...")

    try:
        # Group ထဲရှိ မန်ဘာ အားလုံးကို Direct Fetch ဆွဲယူခြင်း
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)

        total_count = len(members)
        await status_msg.edit_text(f"📣 **{notice}**\n\n👥 စုစုပေါင်း မန်ဘာ **{total_count}** ယောက်အား Tag ခေါ်နေပါပြီ...")

        # ၅ ယောက်တစ်စု ခွဲပြီး Mention Link တကယ်ဝင်အောင် ပို့ပေးခြင်း
        chunk_size = 5
        for i in range(0, total_count, chunk_size):
            chunk = members[i:i + chunk_size]
            mention_text = ""
            for user in chunk:
                name = user.first_name if user.first_name else "User"
                mention_text += f"[{name}](tg://user?id={user.id})  "

            await client.send_message(message.chat.id, mention_text)
            await asyncio.sleep(1.5)  # Telegram Limits မထိစေရန်

    except Exception as e:
        await message.reply_text(f"❌ အမှားဖြစ်ပေါ်ပါသည်: {e}")

@app.on_message(filters.text & ~filters.command(["start", "help", "tagall", "setchance", "boton", "botoff"]))
async def handle_messages(client: Client, message: Message):
    if message.chat.type.value == "private":
        reply = generate_ai_reply()
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
        reply = generate_ai_reply()
        await message.reply_text(reply)

print("Bot စတင်နေပါပြီ...")
app.run()
