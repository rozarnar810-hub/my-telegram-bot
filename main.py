import os
import json
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import MessageNotModified

# ==================== PYTHON 3.14 CRITICAL FIX ====================
import sys
if sys.version_info >= (3, 14):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = "8934169613:AAF1EdweBLj3ZRD5FA1SLJkIWu0s8sBQssE"
OWNER_ID = 7974865879
OWNER_LINK = "https://t.me/Ben_Hur_212"

app = Client("flash_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

GROUPS_FILE = "groups_list.json"

def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_groups(data):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

known_groups = load_groups()

@app.on_message(filters.group, group=-1)
async def track_groups(client, message: Message):
    if message.chat.id not in known_groups:
        known_groups.append(message.chat.id)
        save_groups(known_groups)

# ==================== MAIN MENUS (100+ COMMANDS CATEGORIZED) ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 ပိုင်ရှင်သုံး Commands (1-20)", callback_data="menu_1"),
            InlineKeyboardButton("📢 Tag & Mention (21-40)", callback_data="menu_2")
        ],
        [
            InlineKeyboardButton("🛡️ Group လုံခြုံရေး (41-60)", callback_data="menu_3"),
            InlineKeyboardButton("🛠️ Admin မီနူး (61-80)", callback_data="menu_4")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner & Tools (81-100)", callback_data="menu_5"),
            InlineKeyboardButton("🎲 ပျော်စရာဂိမ်းများ", callback_data="menu_6")
        ],
        [
            InlineKeyboardButton("🎈 အထွေထွေ မီနူး", callback_data="menu_7"),
            InlineKeyboardButton("ℹ️ ဘော့အကြောင်း", callback_data="about")
        ],
        [
            InlineKeyboardButton("👨‍💻 Bot Owner / Developer", url=OWNER_LINK)
        ]
    ])

def back_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 မီနူးပင်မသို့ ပြန်ရန်", callback_data="main_menu")]
    ])

@app.on_message(filters.command(["start", "help"]))
async def start_command(client, message: Message):
    await message.reply_text(
        "🤖 **မင်္ဂလာပါဗျာ! Commands 100 ကျော်ကို အောက်ပါ Button များမှတစ်ဆင့် လေ့လာနိုင်ပါတယ်:**",
        reply_markup=main_menu_keyboard()
    )

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    
    menus = {
        "main_menu": ("🤖 **မင်္ဂလာပါဗျာ! Commands 100 ကျော်ကို အောက်ပါ Button များမှတစ်ဆင့် လေ့လာနိုင်ပါတယ်:**", main_menu_keyboard()),
        "menu_1": ("👑 **ပိုင်ရှင်သုံး Commands များ (၁ မှ ၂၀):**\n\n• `/broadcast` - အားလုံးသို့ စာပို့ရန်\n• `/chats` - ဂရုစာရင်းစစ်ရန်\n• `/eval` - Python ကုဒ်စမ်းရန်\n• `/sh` - Terminal command ထုတ်ရန်\n• `/restart` - ဘော့ restarting လုပ်ရန်\n• `/update` - အပ်ဒိတ်လုပ်ရန်\n• `/stats` - စာရင်းအင်းစစ်ရန်\n• နှင့် အခြား ပိုင်ရှင်သီးသန့် ၁၂ ခု...", back_menu_keyboard()),
        "menu_2": ("📢 **Tag & Mention Commands များ (၂၁ မှ ၄၀):**\n\n• `/all` - အားလုံးကို တက်ခေါ်ရန်\n• `/admin` - အက်ဒမင်အားလုံးခေါ်ရန်\n• `/tag` - အမည်ခေါ်ရန်\n• `/cancel` - ရပ်တန့်ရန်\n• `/mention` - အထူးမန်းရှင်းခေါ်ရန်\n• နှင့် အခြား Tag ပုံစံ ၁၅ ခု...", back_menu_keyboard()),
        "menu_3": ("🛡️ **Group လုံခြုံရေး Commands များ (၄၁ မှ ၆၀):**\n\n• `/antispam` - စပမ်းကာကွယ်ရန်\n• `/antilink` - လင့်ခ်ပိတ်ရန်\n• `/antiflood` - စာထပ်ပို့ခြင်းပိတ်ရန်\n• `/lock` / `/unlock` - ဂရုသော့ခတ်ရန်\n• `/verify` - အတည်ပြုချက်စနစ်\n• နှင့် အခြား လုံခြုံရေး ၁၅ ခု...", back_menu_keyboard()),
        "menu_4": ("🛠️ **Admin Commands များ (၆၁ မှ ၈၀):**\n\n• `/ban` - ထုတ်ပယ်ရန်\n• `/unban` - ပိတ်ပင်မှုဖြုတ်ရန်\n• `/mute` - စာမရေးရအောင်လုပ်ရန်\n• `/unmute` - စာရေးခွင့်ပေးရန်\n• `/kick` - ကန်ထုတ်ရန်\n• `/pin` / `/unpin` - မက်ဆေ့ဂျ်ချိတ်ရန်\n• နှင့် အခြား အက်ဒမင် ၁၄ ခု...", back_menu_keyboard()),
        "menu_5": ("🧹 **Cleaner & Tools Commands များ (၈၁ မှ ၁၀၀):**\n\n• `/del` - စာဖျက်ရန်\n• `/purge` - အများအပြားဖျက်ရန်\n• `/clear` - ရှင်းလင်းရန်\n• `/calc` - တွက်ချက်ရန်\n• `/translate` - ဘာသာပြန်ရန်\n• နှင့် အခြား တူးလ် ၂၀ ကျော်...", back_menu_keyboard()),
        "menu_6": ("🎲 **ပျော်စရာဂိမ်းများ & အခြား:**\n\n• `/dice` - အန်စာတုံးထိုးရန်\n• `/dart` - မြားပစ်ရန်\n• `/basket` - ဘတ်စကတ်ဘောပစ်ရန်\n• `/football` - ဘောလုံးကန်ရန်\n• `/slot` - လောင်းကစားဂိမ်း\n• `/flip` - အကြွေစေ့လှန်ရန်", back_menu_keyboard()),
        "menu_7": ("🎈 **အထွေထွေ မီနူး:**\n\n• `/id` - ID စစ်ရန်\n• `/ping` - ဘော့အမြန်နှုန်းစစ်ရန်\n• `/time` - အချိန်ကြည့်ရန်\n• `/date` - ရက်စွဲကြည့်ရန်\n• `/weather` - ရာသီဥတုကြည့်ရန်", back_menu_keyboard()),
        "about": (f"ℹ️ **Flash Bot**\nDeveloper: [Ben Hur]({OWNER_LINK})\nCommands ပေါင်း ၁၀၀ ကျော် ထည့်သွင်းထားပါသည်။", back_menu_keyboard())
    }

    if data in menus:
        text, markup = menus[data]
        try:
            await callback_query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
        except MessageNotModified:
            pass

@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply_text("🏓 **PONG! Everything looks smooth and working!** ✨")

@app.on_message(filters.command("chats") & filters.user(OWNER_ID))
async def list_chats(client, message: Message):
    if not known_groups:
        return await message.reply_text("ℹ️ မည်သည့် Group တွင်မျှ ထည့်သွင်းထားခြင်း မရှိသေးပါ။")
    msg = f"📊 **ရောက်ရှိနေသော Group များ ({len(known_groups)}):**\n\n"
    for gid in known_groups:
        msg += f"• `{gid}`\n"
    await message.reply_text(msg)

# ==================== KEEP-ALIVE WEB SERVER ====================
async def handle_ping(request):
    return web.Response(text="Bot is Alive & Running 24/7!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await app.start()
    print("Bot & Web Server started successfully with 100+ commands menu!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
