import os
import time
import asyncio
import random
import difflib
import markovify
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# API Credentials
API_ID = 31788996
API_HASH = "0c6714a879b2b1abba75dc4526521ca8"
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 7974865879

DATA_FILE = "chat_memory.txt"
CHAT_SETTINGS = {}
KNOWN_CHATS = set()

# Pyrogram Client
app = Client("my_tag_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🌐 Render Async Web Health Check Server
async def handle_health_check(request):
    return web.Response(text="Bot is Active and Running!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle_health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# 💾 Data Helper Functions
def save_text(text: str):
    if text and len(text.split()) >= 1 and not text.startswith("/"):
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")

def generate_smart_reply(user_message: str) -> str:
    if not os.path.exists(DATA_FILE):
        return "ကျွန်တော် စကားလုံးတွေ မှတ်နေတုန်းပါပဲဗျာ။"

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
        return "မင်္ဂလာပါဗျာ။"

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# 🔘 KEYBOARD BUTTONS UI
def get_help_buttons():
    buttons = [
        [
            InlineKeyboardButton("👑 Owner Tools", callback_data="help_owner"),
            InlineKeyboardButton("🛠️ Admin Tools", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("🎨 AI Image Gen", callback_data="help_ai"),
            InlineKeyboardButton("🎲 Mini Games", callback_data="help_games")
        ],
        [
            InlineKeyboardButton("🎈 General Info", callback_data="help_general")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 မူလ Menu သို့ ပြန်သွားရန်", callback_data="help_main")]])

# 🤖 BOT COMMANDS

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    KNOWN_CHATS.add(message.chat.id)
    text = (
        "👋 **မင်္ဂလာပါ!**\n\n"
        "ကျွန်တော်ကတော့ စာမထောက်ဘဲ အလိုအလျောက် စကားပြန်ပေးနိုင်တဲ့ AI Auto-Chat, Admin Tools နဲ့ Fun Games များ ပါဝင်တဲ့ Bot ဖြစ်ပါတယ်။\n\n"
        "👇 အောက်ပါ Buttons များကို နှိပ်ပြီး Commands များကို လေ့လာနိုင်ပါတယ်ဗျာ။"
    )
    await message.reply_text(text, reply_markup=get_help_buttons())

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text("🤖 **Bot Main Menu - အကြောင်းအရာ ရွေးချယ်ပါ:**", reply_markup=get_help_buttons())

# 🔘 BUTTON CALLBACK HANDLER
@app.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "help_main":
        await query.message.edit_text("🤖 **Bot Main Menu - အကြောင်းအရာ ရွေးချယ်ပါ:**", reply_markup=get_help_buttons())

    elif data == "help_owner":
        text = (
            "👑 **Owner Only Commands (ပိုင်ရှင် သီးသန့်)**\n\n"
            "• `/tagall [စာသား]` - Group မန်ဘာ အားလုံးကို Tag ခေါ်ရန်\n"
            "• `/broadcast [စာသား]` - Group အားလုံးသို့ ကြေညာစာ ပို့ရန်\n"
            "• `/botstats` - Bot သုံးထားသော Group စာရင်း ကြည့်ရန်\n"
            "• `/add [စာသား]` - Bot ကို စကားသစ်များ တိုက်ရိုက် သင်ပေးရန်\n"
            "• `/setchance [0-100]` - Auto ဝင်ပြောမည့် နှုန်းသတ်မှတ်ရန်\n"
            "• `/clearmemory` - မှတ်ထားသော စကားများ ရှင်းထုတ်ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_admin":
        text = (
            "🛠️ **Admin Management Commands**\n\n"
            "• `/ban` - မန်ဘာကို Ban ရန် (Reply ပြန်ပါ)\n"
            "• `/unban [ID]` - Ban ထားသည်ကို ပြန်ဖြုတ်ရန်\n"
            "• `/mute` - စာရိုက်ခွင့် ပိတ်ရန် (Reply ပြန်ပါ)\n"
            "• `/unmute` - စာရိုက်ခွင့် ပြန်ပေးရန် (Reply ပြန်ပါ)\n"
            "• `/kick` - မန်ဘာကို Group မှ ထုတ်ရန် (Reply ပြန်ပါ)\n"
            "• `/pin` - စာကို Pin ရန် | `/unpin` - Pin ဖြုတ်ရန်\n"
            "• `/del` - စာဖျက်ရန် | `/groupinfo` - Group အချက်အလက်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_ai":
        text = (
            "🎨 **AI Image Generator**\n\n"
            "• `/gen [Prompts]` - AI အသုံးပြု၍ ပုံများ ဖန်တီးရန်\n"
            "  _ဥပမာ: `/gen A beautiful sunset over the mountains, 4k`_"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_games":
        text = (
            "🎲 **Mini Games Commands**\n\n"
            "• `/dice` - အန်စာတုံး ပစ်ရန် 🎲\n"
            "• `/dart` - ဒိန်းပစ်ရန် 🎯\n"
            "• `/basket` - ဘက်စကတ်ဘော ပစ်ရန် 🏀\n"
            "• `/bowling` - ဘိုလင်း ပစ်ရန် 🎳\n"
            "• `/football` - ဘောလုံး ကန်ရန် ⚽"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

    elif data == "help_general":
        text = (
            "🎈 **General Commands**\n\n"
            "• `/ping` - Bot မြန်ဆန်မှု (Speed) စစ်ရန်\n"
            "• `/id` - User သို့မဟုတ် Group ID ကြည့်ရန်"
        )
        await query.message.edit_text(text, reply_markup=get_back_button())

# 🛠️ ADMIN COMMAND HANDLERS
@app.on_message(filters.command("ban"))
async def ban_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Ban ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.ban_member(user_id)
        await message.reply_text(f"⛔️ User `{user_id}` ကို Group မှ Ban လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("unban"))
async def unban_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply_text("💡 အသုံးပြုပုံ: `/unban 12345678` (User ID ထည့်ပေးပါ)")
        return
    try:
        user_id = int(args[1])
        await message.chat.unban_member(user_id)
        await message.reply_text(f"✅ User `{user_id}` အား Ban ဖြုတ်ပေးလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("mute"))
async def mute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Mute လုပ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        await message.chat.restrict_member(user_id, ChatPermissions())
        await message.reply_text(f"🔇 User `{user_id}` ၏ စာရိုက်ခွင့်ကို ပိတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("unmute"))
async def unmute_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Unmute လုပ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        await message.chat.restrict_member(
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply_text(f"🔊 User `{user_id}` အား စာပြန်ရိုက်ခွင့် ပေးလိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("kick"))
async def kick_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Group မှ ထုတ်ချင်သည့် User ရဲ့ စာကို Reply ပြန်ပါ။")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await message.chat.ban_member(user_id)
        await message.chat.unban_member(user_id)
        await message.reply_text(f"👞 User `{user_id}` ကို Group မှ ထုတ်ပစ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# 🎨 AI IMAGE GENERATOR
@app.on_message(filters.command("gen"))
async def gen_cmd(client: Client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("💡 အသုံးပြုပုံ: `/gen a cat wearing sunglasses`")
        return

    prompt = message.text.split(maxsplit=1)[1]
    msg = await message.reply_text("🎨 AI မှ ပုံဖန်တီးပေးနေပါသည် ခဏစောင့်ပေးပါ...")

    try:
        encoded_prompt = prompt.replace(" ", "%20")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        await message.reply_photo(photo=image_url, caption=f"✨ **Prompt:** `{prompt}`")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ ပုံဖန်တီးရာတွင် အမှားဖြစ်ပေါ်ပါသည်: {e}")

# 🎲 GAMES HANDLERS
@app.on_message(filters.command("dice"))
async def dice_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎲")

@app.on_message(filters.command("dart"))
async def dart_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎯")

@app.on_message(filters.command("basket"))
async def basket_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🏀")

@app.on_message(filters.command("bowling"))
async def bowling_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="🎳")

@app.on_message(filters.command("football"))
async def football_cmd(client: Client, message: Message):
    await client.send_dice(message.chat.id, emoji="⚽")

# 🎈 UTILITIES & GENERAL
@app.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start_time = time.time()
    msg = await message.reply_text("🏓 Pong!")
    end_time = time.time()
    ms = round((end_time - start_time) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⚡️ Speed: `{ms} ms`")

@app.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        await message.reply_text(f"👤 **Name:** {target.first_name}\n🆔 **User ID:** `{target.id}`")
    else:
        await message.reply_text(f"💬 **Group ID:** `{message.chat.id}`\n👤 **Your ID:** `{message.from_user.id}`")

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
        await message.reply_text("💡 အသုံးပြုပုံ: `/setchance 50` (0 မှ 100 အထိ)")
        return

    chance = int(args[1])
    if 0 <= chance <= 100:
        CHAT_SETTINGS.setdefault(message.chat.id, {})["chance"] = chance
        await message.reply_text(f"🎯 Bot အလိုအလျောက် ဝင်ပြောမည့် နှုန်းကို {chance}% သို့ ပြောင်းလိုက်ပါပြီ။")

@app.on_message(filters.command("clearmemory"))
async def clearmemory_cmd(client: Client, message: Message):
    if not is_owner(message.from_user.id):
        await message.reply_text("❌ ဤ Command ကို Bot ပိုင်ရှင် (Owner) သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        await message.reply_text("🗑️ မှတ်ထားသော စကားလုံး အားလုံးကို ရှင်းထုတ်ပြီးပါပြီ။")
    else:
        await message.reply_text("မှတ်တမ်းဖိုင် မရှိသေးပါဗျာ။")

@app.on_message(filters.command("pin"))
async def pin_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 Pin ချင်တဲ့ စာကို Reply ပြန်ပြီး `/pin` လို့ ရိုက်ပါ။")
        return
    try:
        await message.reply_to_message.pin()
        await message.reply_text("📌 စာကို Pin လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Pin လုပ်၍ မရပါ: {e}")

@app.on_message(filters.command("unpin"))
async def unpin_cmd(client: Client, message: Message):
    try:
        await client.unpin_chat_message(message.chat.id)
        await message.reply_text("📌 Pin ထားသည်ကို ပြန်ဖြုတ်လိုက်ပါပြီ။")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("del"))
async def del_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("💡 ဖျက်ချင်သည့် စာကို Reply ပြန်ပြီး `/del` လို့ ရိုက်ပါ။")
        return
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply_text(f"❌ စာဖျက်၍ မရပါ: {e}")

@app.on_message(filters.command("groupinfo"))
async def groupinfo_cmd(client: Client, message: Message):
    if message.chat.type.value == "private":
        await message.reply_text("ဒီ Command က Group ထဲမှာပဲ သုံးလို့ရပါတယ်။")
        return
    
    chat = message.chat
    info = (
        f"🏰 **Group အချက်အလက်**\n\n"
        f"• **အမည်:** {chat.title}\n"
        f"• **Group ID:** `{chat.id}`\n"
        f"• **Type:** {chat.type.value.capitalize()}\n"
        f"• **Members Count:** {await client.get_chat_members_count(chat.id)}"
    )
    await message.reply_text(info)

# ⭐️ AUTO CHAT LISTENER
ALL_COMMANDS = [
    "start", "help", "ping", "id", "tagall", "broadcast", "botstats", 
    "add", "setchance", "clearmemory", "pin", "unpin", "del", "groupinfo",
    "ban", "unban", "mute", "unmute", "kick", "gen",
    "dice", "dart", "basket", "bowling", "football"
]

@app.on_message(filters.text & ~filters.command(ALL_COMMANDS))
async def handle_messages(client: Client, message: Message):
    if not message.chat or not message.text:
        return

    KNOWN_CHATS.add(message.chat.id)

    me = await client.get_me()
    if message.from_user and message.from_user.id == me.id:
        return

    save_text(message.text)
    
    chat_id = message.chat.id
    settings = CHAT_SETTINGS.get(chat_id, {"chance": 100})
    auto_chance = settings.get("chance", 100)

    if auto_chance > 0 and random.randint(1, 100) <= auto_chance:
        reply = generate_smart_reply(message.text)
        await message.reply_text(reply)

# 🚀 MAIN RUNNER
async def main():
    await start_web_server()
    print("Web Server စတင်ပါပြီ...")
    await app.start()
    print("Bot စတင်နေပါပြီ...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
