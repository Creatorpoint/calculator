import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from flask import Flask
from threading import Thread
import os

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import *

# =========================================================
# WEB SERVER FOR RENDER
# =========================================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Professional Calculator Bot Running Successfully"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

# =========================================================
# TELEGRAM BOT
# =========================================================

app = Client(
    "ProfessionalCalculatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=100,
    sleep_threshold=30
)

# =========================================================
# CONFIG
# =========================================================

START_IMAGE = "https://files.catbox.moe/splh4m.jpg"

USERS_FILE = "users.txt"

if not os.path.exists(USERS_FILE):
    open(USERS_FILE, "w").close()

user_data = {}

# =========================================================
# SAVE USER
# =========================================================

def save_user(user_id):

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    if str(user_id) not in users:
        with open(USERS_FILE, "a") as file:
            file.write(f"{user_id}\n")

# =========================================================
# FORCE JOIN CHECK
# =========================================================

async def check_force_join(client, user_id):

    try:

        channel = await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

        group = await client.get_chat_member(
            FORCE_GROUP,
            user_id
        )

        if channel.status in ["left", "kicked"]:
            return False

        if group.status in ["left", "kicked"]:
            return False

        return True

    except:
        return False

# =========================================================
# PROFESSIONAL BUTTONS
# =========================================================

calculator_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("➕", callback_data="+"),
            InlineKeyboardButton("➖", callback_data="-"),
            InlineKeyboardButton("✖️", callback_data="*"),
            InlineKeyboardButton("➗", callback_data="/")
        ],
        [
            InlineKeyboardButton("7", callback_data="7"),
            InlineKeyboardButton("8", callback_data="8"),
            InlineKeyboardButton("9", callback_data="9")
        ],
        [
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5"),
            InlineKeyboardButton("6", callback_data="6")
        ],
        [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3")
        ],
        [
            InlineKeyboardButton(".", callback_data="."),
            InlineKeyboardButton("0", callback_data="0"),
            InlineKeyboardButton("=", callback_data="=")
        ],
        [
            InlineKeyboardButton(
                "🗑 Clear",
                callback_data="clear"
            )
        ]
    ]
)

# =========================================================
# START COMMAND
# =========================================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    user_id = message.from_user.id

    save_user(user_id)

    joined = await check_force_join(client, user_id)

    # ================= FORCE JOIN ================= #

    if not joined:

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{FORCE_CHANNEL.replace('@', '')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "👥 Join Group",
                        url=f"https://t.me/{FORCE_GROUP.replace('@', '')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ Verify Join",
                        callback_data="check_join"
                    )
                ]
            ]
        )

        return await message.reply_photo(
            photo=START_IMAGE,
            caption=(
                "✨ **Welcome To Professional Calculator Bot**\n\n"
                "⚠️ To Use This Bot,\n"
                "Please Join Our Official Channel & Group."
            ),
            reply_markup=buttons
        )

    # ================= MAIN MENU ================= #

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨ **Professional Calculator Activated**\n\n"
            "⚡ Fast Response\n"
            "🧮 Advanced Calculator\n"
            "👥 Group Support Enabled\n\n"
            "👇 Use Buttons Below"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# VERIFY JOIN
# =========================================================

@app.on_callback_query(filters.regex("check_join"))
async def verify_join(client, callback_query):

    user_id = callback_query.from_user.id

    joined = await check_force_join(client, user_id)

    if not joined:

        return await callback_query.answer(
            "❌ Join Channel & Group First",
            show_alert=True
        )

    await callback_query.message.edit_caption(
        caption=(
            "✅ **Verification Successful**\n\n"
            "🧮 Calculator Ready To Use"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# BUTTON CALCULATOR
# =========================================================

@app.on_callback_query()
async def calculator(client, callback_query):

    data = callback_query.data

    if data == "check_join":
        return

    user_id = callback_query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = ""

    expression = user_data[user_id]

    # ================= CLEAR ================= #

    if data == "clear":
        expression = ""

    # ================= RESULT ================= #

    elif data == "=":

        try:
            result = f"{eval(expression):,}"
            expression = result

        except:
            expression = "Error"

    # ================= INPUT ================= #

    else:
        expression += data

    user_data[user_id] = expression

    try:

        await callback_query.message.edit_caption(
            caption=(
                "🧮 **Professional Calculator**\n\n"
                f"`{expression}`"
            ),
            reply_markup=calculator_buttons
        )

    except:
        pass

# =========================================================
# GROUP & PRIVATE TEXT CALCULATOR
# =========================================================

@app.on_message(
    filters.text &
    ~filters.command(
        ["start", "broadcast", "users"]
    )
)
async def text_calculator(client, message):

    try:

        text = message.text.strip()

        allowed = "0123456789+-*/().% "

        for char in text:

            if char not in allowed:
                return

        result = eval(text)

        await message.reply_text(
            "🧮 **Calculator Result**\n\n"
            f"📥 Expression : `{text}`\n"
            f"📤 Result : `{result}`"
        )

    except:
        pass

# =========================================================
# BROADCAST SYSTEM
# =========================================================

@app.on_message(
    filters.command("broadcast") &
    filters.user(OWNER_ID)
)
async def broadcast_message(client, message):

    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply To Any Message To Broadcast"
        )

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    success = 0
    failed = 0

    progress = await message.reply_text(
        "📢 Broadcasting Message..."
    )

    for user in users:

        try:

            await message.reply_to_message.copy(
                int(user)
            )

            success += 1

        except:
            failed += 1

    await progress.edit_text(
        "✅ Broadcast Completed\n\n"
        f"✔ Success : {success}\n"
        f"❌ Failed : {failed}"
    )

# =========================================================
# USERS COUNT
# =========================================================

@app.on_message(
    filters.command("users") &
    filters.user(OWNER_ID)
)
async def users_count(client, message):

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    await message.reply_text(
        f"👥 Total Users : {len(users)}"
    )

# =========================================================
# HELP COMMAND
# =========================================================

@app.on_message(filters.command("help"))
async def help_command(client, message):

    await message.reply_text(
        "📚 **Bot Commands**\n\n"
        "/start - Start Bot\n"
        "/help - Help Menu\n"
        "/users - Total Users\n"
        "/broadcast - Broadcast Message\n\n"
        "🧮 Send Any Math Expression:\n"
        "`5+5`\n"
        "`100/5`\n"
        "`8*7`"
    )

# =========================================================
# BOT START
# =========================================================

print("Professional Calculator Bot Started Successfully")

app.run()
