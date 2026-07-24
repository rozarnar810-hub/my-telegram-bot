import os
import asyncio
import random
import threading
import difflib
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

# API Credentials
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}

# Bot ရောက်ဖူးသမျှ Group/Chat ID များကို သိမ်းဆည်းရန်
KNOWN_CHATS = set()

app = Client("my_tag_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# စာသားများ Auto Save ပြုလုပ်ခြင်း
def save_text(text: str):
    if len(text.split()) >= 1 and not text.startswith("/"):
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")

# မန်ဘာပြောသော စကားလုံးနှင့် မှတ်ထားသော စာများထဲမှ အနီးစပ်ဆုံး ရှာ၍ ပြန်ဖြေပေးသည့် စနစ်
def generate_smart_reply(user_message: str) -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲ၊ Group ထဲမှာ စကားများများ ပြောပေးကြပါ။"

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            return "စကားလုံး အချက်အလက် မရှိသေးပါဗျာ။"

        # 1. တိုက်ရိုက် သို့မဟုတ် အနီးစပ်ဆုံး တူညီသည့် စာကြောင်းကို စစ်ဆေးခြင်း (Similarity Check)
        matches = difflib.get_close_matches(user_message, lines, n=3, cutoff=0.3)
        if matches:
            return random.choice(matches)

        # 2. မန်ဘာပြောသည့် စကားလုံး အချို့ ပါဝင်နေသည့် စာကြောင်းများ ရှာခြင်း
        matched_lines = [l for l in lines if any(word in l for word in user_message.split() if len(word) > 2)]
        if matched_lines:
            return random.choice(matched_lines)

        # 3. အနီးစပ်ဆုံး မတွေ့ပါက Markovify AI ဖြင့် စကားကြောင်း ဆက်ပြီး ပြန်ဖြေခြင်း
        text_data = "\n".join(lines)
        text_model = markovify.NewlineText(text_data, state_size=1)
        reply = text_model.make_sentence(tries=50)

        return reply if reply else random.choice(lines)

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
    KNOWN_CHATS.add(message.chat.id)
    await message.reply_text("မင်္ဂလာပါ။ Group Member အားလုံးကို အလိုအလျောက် စစ်ဆေးပြီး Tag ခေါ်ပေးနိုင်သော AI Bot ဖြစ်ပါတယ်ဗျာ။ /help ကို နှိပ်ပါ။")

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "🤖 **Bot အသုံးပြုနိုင်သော Command များ**\n\n"
        "📢 **Tag စနစ်:**\n"
        "• `/tagall [စာသား]` - Group ထဲရှိ မန်ဘာ အားလုံးကို အလိုအလျောက် စစ်ဆေးပြီး Mention ခေါ်ရန်\n\n"
        "💬 **AI & Group Management:**\n"
        "• `/setchance [0-100]` - Auto ပြောမည့် နှုန်းသတ်မှတ်ရန်\n"
        "• `/boton` / `/botoff` - Bot ပိတ်/ဖွင့်ရန်\n"
        "• `/add [စာသား]` - Bot ကို စကားလုံး တိုက်ရိုက် သင်ပေးရန်\n\n"
        "👑 **Admin / Owner Only:**\n"
        "• `/broadcast [စာသား]` - Bot ရောက်နေသည့် Group အားလုံးသို့ ကြေညာစာ ပို့ရန်\n"
        "• `/botstats` - Bot ကို Group ဘယ်နှစ်ခုမှာ သုံးထားလဲ စစ်ရန်"
    )
    await message.reply_text(help_text)

# ⭐️ မန်ဘာ အားလုံးကို Auto စစ်ဆေးပြီး Tag ခေါ်သည့် စနစ်
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

# 📢 ကြော်ငြာစာ ပို့သည့် စနစ် (Broadcast to All Groups)
@app.on_message(filters.command("broadcast"))
async def broadcast_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။")
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

# 📊 Bot ကို Group ဘယ်နှစ်ခုမှာ သုံးထားလဲ စစ်ဆေးသည့် စနစ်
@app.on_message(filters.command("botstats"))
async def botstats_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။")
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

# 💬 စကားလုံး သင်ပေးသည့် Command
@app.on_message(filters.command("add"))
async def add_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/add မင်္ဂလာပါဗျာ`")
        return
    text_to_add = message.text.split(maxsplit=1)[1]
    save_text(text_to_add)
    await message.reply_text(f"✅ စကားလုံး မှတ်ယူလိုက်ပါပြီ: \"{text_to_add}\"")

# ⚙️ Auto Reply Chance သတ်မှတ်ခြင်း
@app.on_message(filters.command("setchance"))
async def setchance_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("❌ Admin သာလျှင် Chance သတ်မှတ်ပိုင်ခွင့် ရှိပါတယ်။")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply_text("💡 အသုံးပြုပုံ: `/setchance 20` (0 မှ 100 အထိ)")
        return

    chance = int(args[1])
    if 0 <= chance <= 100:
        CHAT_SETTINGS.setdefault(message.chat.id, {})["chance"] = chance
        await message.reply_text(f"🎯 Bot အလိုအလျောက် ဝင်ပြောမည့် နှုန်းကို {chance}% သို့ ပြောင်းလိုက်ပါပြီ။")

# 💬 စကားပြန်ပြောခြင်း နှင့် စာAuto Save လုပ်ခြင်း
@app.on_message(filters.text & ~filters.command(["start", "help", "tagall", "broadcast", "botstats", "add", "setchance", "boton", "botoff"]))
async def handle_messages(client: Client, message: Message):
    # Chat ID အား မှတ်ထားခြင်း
    KNOWN_CHATS.add(message.chat.id)

    if message.chat.type.value == "private":
        reply = generate_smart_reply(message.text)
        await message.reply_text(reply)
        return

    # မန်ဘာ ပြောသော စကားကို Auto Save ပြုလုပ်ခြင်း
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

    # Bot ကို Mention ခေါ်မှ/Reply ပြန်မှ သို့မဟုတ် Auto Chance မိမှ ပြန်ဖြေမည်
    if is_mentioned or is_reply or should_reply:
        reply = generate_smart_reply(message.text)
        await message.reply_text(reply)

print("Bot စတင်နေပါပြီ...")
app.run()
