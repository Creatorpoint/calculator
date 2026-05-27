import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
from flask import Flask
from threading import Thread
import os
import math

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import *

# =========================================================
# WEB SERVER FOR RENDER WEB SERVICE
# =========================================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Professional Calculator Bot Is Running Successfully"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

# =========================================================
# TELEGRAM BOT CLIENT
# =========================================================

app = Client(
    "ProfessionalCalculatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
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
# SAVE USERS
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
        await client.get_chat_member(FORCE_CHANNEL, user_id)
        await client.get_chat_member(FORCE_GROUP, user_id)
        return True

    except:
        return False

# =========================================================
# CALCULATOR BUTTONS
# =========================================================

calculator_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("7", callback_data="7"),
            InlineKeyboardButton("8", callback_data="8"),
            InlineKeyboardButton("9", callback_data="9"),
            InlineKeyboardButton("÷", callback_data="/")
        ],
        [
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5"),
            InlineKeyboardButton("6", callback_data="6"),
            InlineKeyboardButton("×", callback_data="*")
        ],
        [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3"),
            InlineKeyboardButton("−", callback_data="-")
        ],
        [
            InlineKeyboardButton("0", callback_data="0"),
            InlineKeyboardButton(".", callback_data="."),
            InlineKeyboardButton("=", callback_data="="),
            InlineKeyboardButton("+", callback_data="+")
        ],
        [
            InlineKeyboardButton("🗑 Clear", callback_data="clear")
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
                "⚠️ To Continue Using This Bot,\n"
                "Please Join Our Official Channel & Group First."
            ),
            reply_markup=buttons
        )

    # ================= MAIN MENU ================= #

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨ **Professional Calculator Bot Activated**\n\n"
            "🧮 Fast • Stylish • Advanced Calculator\n\n"
            "👇 Use Buttons Below"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# FORCE JOIN VERIFY
# =========================================================

@app.on_callback_query(filters.regex("check_join"))
async def verify_join(client, callback_query):

    user_id = callback_query.from_user.id

    joined = await check_force_join(client, user_id)

    if not joined:
        return await callback_query.answer(
            "❌ Please Join Channel & Group First",
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
# CALCULATOR SYSTEM
# =========================================================

@app.on_callback_query()
async def calculator_system(client, callback_query):

    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "check_join":
        return

    if user_id not in user_data:
        user_data[user_id] = ""

    expression = user_data[user_id]

    # ================= CLEAR ================= #

    if data == "clear":
        expression = ""

    # ================= RESULT ================= #

    elif data == "=":

        try:
            result = str(eval(expression))
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
# BROADCAST SYSTEM
# =========================================================

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
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
        "📢 Broadcasting Message To Users..."
    )

    for user in users:

        try:
            await message.reply_to_message.copy(int(user))
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

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_count(client, message):

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    await message.reply_text(
        f"👥 Total Bot Users : {len(users)}"
    )

# =========================================================
# BOT START
# =========================================================

print("Professional Calculator Bot Started Successfully")

app.run()
