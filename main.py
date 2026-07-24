import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ ကျွန်တော်က Gemini AI နဲ့ ချိတ်ဆက်ထားတဲ့ Telegram Bot ဖြစ်ပါတယ်။ မေးချင်တာတွေကို စာပို့ပြီး မေးမြန်းနိုင်ပါတယ်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if not client:
        await update.message.reply_text("Error: GEMINI_API_KEY ထည့်သွင်းထားခြင်း မရှိသေးပါ။")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Model နာမည်ကို gemini-1.5-flash သို့ ပြောင်းလဲထားပါသည်
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_text,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        await update.message.reply_text("တောင်းပန်ပါတယ်၊ စာပြန်စဉ် အမှားတစ်ခု ဖြစ်ပေါ်သွားပါသည်။")

def main():
    if not TELEGRAM_TOKEN:
        print("Error: BOT_TOKEN လိုအပ်နေပါသည်။")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot စတင်ပွင့်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
