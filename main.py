import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging သတ်မှတ်ခြင်း
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render ရဲ့ Environment Variables ထဲကနေ BOT_TOKEN ကို အလိုအလျောက် ဖတ်ယူမည်
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ Render Cloud Server ပေါ်ကနေ Bot အလုပ်လုပ်နေပါပြီ!")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN လိုအပ်နေပါသည်။ Render Environment Variables ထဲမှာ ထည့်ပေးပါ။")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot စတင်ပွင့်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
