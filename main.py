import os
import logging
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import markovify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}
KNOWN_CHATS = set()

# မန်ဘာများ၏ ID နှင့် နာမည်များကို မှတ်ထားမည့် Database (In-Memory)
GROUP_MEMBERS = {}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Active")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type == "private":
        return True
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["creator", "administrator"]

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

        if reply:
            return reply
        else:
            lines = text_data.strip().split("\n")
            return random.choice(lines)
            
    except Exception as e:
        logging.error(f"Error generating reply: {e}")
        return "စကားပြန်ပြောဖို့ အချက်အလက် နည်းနေသေးလို့ပါဗျာ။"

# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    KNOWN_CHATS.add(update.effective_chat.id)
    await update.message.reply_text("မင်္ဂလာပါ။ AI Auto-Reply & Tag Bot ဖြစ်ပါတယ်။ /help ကို နှိပ်ပြီး Command များ ကြည့်နိုင်ပါတယ်။")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Bot အသုံးပြုနိုင်သော Command များ*\n\n"
        "💬 *အထွေထွေ Command များ:*\n"
        "• /start - Bot စတင်ရန်\n"
        "• /help - Command များ ကြည့်ရန်\n"
        "• /stats - မှတ်ထားသော စကားလုံး အရေအတွက်ကြည့်ရန်\n"
        "• /add [စာသား] - Bot ကို စကားလုံး တိုက်ရိုက် သင်ပေးရန်\n\n"
        "📢 *Group Admin & Management:*\n"
        "• /tagall [စာသား] - Member အားလုံးကို တကယ် Notification ဝင်အောင် Tag ခေါ်ရန်\n"
        "• /setchance [0-100] - Bot Auto ဝင်ပြောမည့် % သတ်မှတ်ရန်\n"
        "• /boton / /botoff - Bot စကားပြောစနစ် ပိတ်/ဖွင့် ရန်\n"
        "• /broadcast [စာသား] - ကြေညာချက် ပို့ရန် (Admin Only)\n"
        "• /resetmemory - Memory ဖျက်ရန်"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Barker Tag Bot ကဲ့သို့ မန်ဘာများကို ၅ ယောက်တစ်စု တကယ် Notification ဝင်အောင် Tag ခေါ်သည့် စနစ်
async def tagall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin သာလျှင် Member များကို Tag ခေါ်နိုင်ပါတယ်။")
        return
    
    chat_id = update.effective_chat.id
    notice = " ".join(context.args) if context.args else "လူစုံတက်စုံ သတိပေးချက်!"
    
    members = GROUP_MEMBERS.get(chat_id, {})
    if not members:
        await update.message.reply_text("⚠️ Tag ခေါ်ရန် မန်ဘာ စာရင်း မရှိသေးပါ။ မန်ဘာများ Group ထဲတွင် စာတစ်ကြောင်းစီ စကားပြောထားပေးဖို့ လိုအပ်ပါတယ်ဗျာ။")
        return

    member_items = list(members.items())
    chunk_size = 5  # တစ်ခါ ပို့ရင် ၅ ယောက်စီ ခွဲပြီး ပို့မည်
    
    await update.message.reply_text(f"📣 *{notice}*\n\nTag ခေါ်ခြင်း စတင်နေပါပြီ...", parse_mode="Markdown")

    for i in range(0, len(member_items), chunk_size):
        chunk = member_items[i:i + chunk_size]
        mention_text = ""
        for user_id, name in chunk:
            # တကယ် Notification ဝင်စေသည့် Text Mention Link
            mention_text += f"[{name}](tg://user?id={user_id})  "

        try:
            await context.bot.send_message(chat_id=chat_id, text=mention_text, parse_mode="Markdown")
        except Exception:
            pass

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။")
        return
    if not context.args:
        await update.message.reply_text("💡 အသုံးပြုပုံ: `/broadcast သတင်းလွှာ စာသား`", parse_mode="Markdown")
        return

    msg = " ".join(context.args)
    count = 0
    for chat_id in KNOWN_CHATS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 *ကြေညာချက်:*\n\n{msg}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Chat ပေါင်း {count} ခုသို့ စာကြေညာချက် ပို့ပြီးပါပြီ။")

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💡 အသုံးပြုပုံ: `/add မင်္ဂလာပါဗျာ`", parse_mode="Markdown")
        return
    text_to_add = " ".join(context.args)
    save_text(text_to_add)
    await update.message.reply_text(f"✅ စကားလုံး မှတ်ယူလိုက်ပါပြီ: \"{text_to_add}\"")

async def setchance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin သာလျှင် Chance သတ်မှတ်ပိုင်ခွင့် ရှိပါတယ်။")
        return
    chat_id = update.effective_chat.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("💡 အသုံးပြုပုံ: `/setchance 20` (0 မှ 100 အထိ)", parse_mode="Markdown")
        return
    chance = int(context.args[0])
    if 0 <= chance <= 100:
        CHAT_SETTINGS.setdefault(chat_id, {})["chance"] = chance
        await update.message.reply_text(f"🎯 Bot အလိုအလျောက် ဝင်ပြောမည့် နှုန်းကို {chance}% သို့ ပြောင်းလိုက်ပါပြီ။")
    else:
        await update.message.reply_text("0 မှ 100 အကြား ကိန်းဂဏန်းသာ ထည့်ပါ။")

async def toggle_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin သာလျှင် ပိတ်/ဖွင့် ပြုလုပ်နိုင်ပါတယ်။")
        return
    chat_id = update.effective_chat.id
    command = update.message.text.split()[0].lower()
    
    if "boton" in command:
        CHAT_SETTINGS.setdefault(chat_id, {})["enabled"] = True
        await update.message.reply_text("✅ Bot စကားပြောစနစ်ကို ဖွင့်လိုက်ပါပြီ။")
    else:
        CHAT_SETTINGS.setdefault(chat_id, {})["enabled"] = False
        await update.message.reply_text("❌ Bot စကားပြောစနစ်ကို ပိတ်လိုက်ပါပြီ။")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        await update.message.reply_text(f"📊 လက်ရှိ Bot မှတ်ထားသော စာကြောင်းပေါင်း: {len(lines)} ကြောင်း ရှိပါပြီ။")
    else:
        await update.message.reply_text("📊 လက်ရှိတွင် မှတ်ထားသော စကားလုံး မရှိသေးပါ။")

async def resetmemory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin သာလျှင် Memory ဖျက်ပိုင်ခွင့် ရှိပါတယ်။")
        return
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        await update.message.reply_text("🗑️ မှတ်ထားသော စကားလုံးများ အားလုံးကို ဖျက်လိုက်ပါပြီ။")
    else:
        await update.message.reply_text("ဖျက်စရာ အချက်အလက် မရှိပါ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    KNOWN_CHATS.add(chat_id)

    # မန်ဘာများ စာရိုက်လိုက်သည်နှင့် ID/Name ကို သိမ်းဆည်းခြင်း
    if user and not user.is_bot:
        GROUP_MEMBERS.setdefault(chat_id, {})[user.id] = user.first_name
    
    settings = CHAT_SETTINGS.get(chat_id, {"enabled": True, "chance": 0})
    if not settings.get("enabled", True):
        return

    user_text = update.message.text
    save_text(user_text)

    bot_username = context.bot.username
    is_mentioned = bot_username and f"@{bot_username}" in user_text
    is_reply_to_bot = (
        update.message.reply_to_message and 
        update.message.reply_to_message.from_user.id == context.bot.id
    )
    is_private = update.effective_chat.type == "private"

    auto_chance = settings.get("chance", 0)
    should_random_reply = random.randint(1, 100) <= auto_chance if auto_chance > 0 else False

    if is_mentioned or is_reply_to_bot or is_private or should_random_reply:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        reply = generate_ai_reply()
        await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN:
        print("Error: BOT_TOKEN လိုအပ်နေပါသည်။")
        return

    threading.Thread(target=run_health_check_server, daemon=True).start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("tagall", tagall_command))
    app.add_handler(CommandHandler("setchance", setchance_command))
    app.add_handler(CommandHandler("boton", toggle_bot_command))
    app.add_handler(CommandHandler("botoff", toggle_bot_command))
    app.add_handler(CommandHandler("resetmemory", resetmemory_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot စတင်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
