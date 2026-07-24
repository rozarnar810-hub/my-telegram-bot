import os
import logging
import markovify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "chat_memory.txt"

# Member တွေပြောတဲ့ စာများကို သိမ်းဆည်းပေးသည့် Function
def save_text(text: str):
    # စာလုံး အနည်းဆုံး ၃ လုံးပါမှ မှတ်မည်
    if len(text.split()) >= 2:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

# မှတ်ထားသော စာများမှ AI ပုံစံ စကားစု ပြန်လည်ထုတ်ပေးသည့် Function
def generate_ai_reply() -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲ၊ Group ထဲမှာ စကားများများ ပြောပေးကြပါ။"

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            text_data = f.read()

        if len(text_data.strip()) == 0:
            return "စကားလုံး အချက်အလက် မရှိသေးပါဗျာ။"

        # Markov Chain AI Model တည်ဆောက်ခြင်း
        text_model = markovify.NewlineText(text_data, state_size=1)
        reply = text_model.make_sentence(tries=100)

        if reply:
            return reply
        else:
            # စကားစု မဖွဲ့နိုင်သေးပါက မှတ်ထားသည်များထဲမှ တစ်ကြောင်း ပြန်ထုတ်ပေးခြင်း
            lines = text_data.strip().split("\n")
            import random
            return random.choice(lines)
            
    except Exception as e:
        logging.error(f"Error generating reply: {e}")
        return "စကားပြန်ပြောဖို့ အချက်အလက် နည်းနေသေးလို့ပါဗျာ။"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ အဖွဲ့ဝင်များ စကားပြောတာကို လေ့လာပြီး AI ပုံစံ ပြန်လည်စကားပြောပေးမယ့် Bot ဖြစ်ပါတယ်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # ၁။ Member ပြောလိုက်တဲ့ စကားကို File ထဲ Auto မှတ်ထားမည်
    save_text(user_text)

    # ၂။ Bot ကို Tag လုပ်ပြီး ခေါ်ရင် သို့မဟုတ် Bot ကို Reply ပြန်ရင် AI ပုံစံ ပြန်ဖြေမည်
    bot_username = context.bot.username
    is_mentioned = f"@{bot_username}" in user_text
    is_reply_to_bot = (
        update.message.reply_to_message and 
        update.message.reply_to_message.from_user.id == context.bot.id
    )

    # Private Chat (Direct Chat) မှာဆိုရင် အမြဲ စာပြန်မည်
    is_private = update.effective_chat.type == "private"

    if is_mentioned or is_reply_to_bot or is_private:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        reply = generate_ai_reply()
        await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN:
        print("Error: BOT_TOKEN လိုအပ်နေပါသည်။")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Markov Learning Bot စတင်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
