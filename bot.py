import asyncio
import os
from flask import Flask
from threading import Thread

# =========================================================
# FIX PYTHON 3.14 PYROGRAM ERROR
# =========================================================

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# =========================================================
# IMPORTS
# =========================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import *

# =========================================================
# WEB SERVER FOR RENDER
# =========================================================

web = Flask(__name__)

@web.route("/")
def home():
    return "Prime Calculator Bot Running Successfully"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

# =========================================================
# BOT CLIENT
# =========================================================

app = Client(
    "PrimeCalculator",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=200,
    sleep_threshold=30
)

# =========================================================
# FILES
# =========================================================

USERS_FILE = "users.txt"
GROUPS_FILE = "groups.txt"

if not os.path.exists(USERS_FILE):
    open(USERS_FILE, "w").close()

if not os.path.exists(GROUPS_FILE):
    open(GROUPS_FILE, "w").close()

# =========================================================
# START IMAGE
# =========================================================

START_IMAGE = "https://files.catbox.moe/splh4m.jpg"

# =========================================================
# USER DATA
# =========================================================

calculator_data = {}

# =========================================================
# SAVE USER
# =========================================================

def save_user(user_id):

    user_id = str(user_id)

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    if user_id not in users:

        with open(USERS_FILE, "a") as f:
            f.write(user_id + "\n")

# =========================================================
# SAVE GROUP
# =========================================================

def save_group(group_id):

    group_id = str(group_id)

    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()

    if group_id not in groups:

        with open(GROUPS_FILE, "a") as f:
            f.write(group_id + "\n")

# =========================================================
# FORCE JOIN CHECK
# =========================================================

async def check_force_join(user_id):

    try:
        await app.get_chat_member(FORCE_CHANNEL, user_id)
    except:
        return False

    try:
        await app.get_chat_member(FORCE_GROUP, user_id)
    except:
        return False

    return True

# =========================================================
# PROFESSIONAL CALCULATOR BUTTONS
# =========================================================

calculator_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("7", callback_data="7"),
            InlineKeyboardButton("8", callback_data="8"),
            InlineKeyboardButton("9", callback_data="9"),
            InlineKeyboardButton("➗", callback_data="/")
        ],
        [
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5"),
            InlineKeyboardButton("6", callback_data="6"),
            InlineKeyboardButton("✖️", callback_data="*")
        ],
        [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3"),
            InlineKeyboardButton("➖", callback_data="-")
        ],
        [
            InlineKeyboardButton(".", callback_data="."),
            InlineKeyboardButton("0", callback_data="0"),
            InlineKeyboardButton("=", callback_data="="),
            InlineKeyboardButton("➕", callback_data="+")
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
async def start(client, message):

    user_id = message.from_user.id

    save_user(user_id)

    joined = await check_force_join(user_id)

    # =====================================================
    # FORCE JOIN SYSTEM
    # =====================================================

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
                        callback_data="verify_join"
                    )
                ]
            ]
        )

        return await message.reply_photo(
            photo=START_IMAGE,
            caption=(
                "✨ **WELCOME TO PRIME CALCULATOR** ✨\n\n"
                "⚠️ Access Locked\n"
                "📢 Join Our Official Channel & Group\n"
                "✅ Then Click Verify Button\n\n"
                "🚀 Fast Response\n"
                "🧮 Advanced Calculator\n"
                "👥 Group Support\n"
                "📡 Broadcast System\n\n"
                "👨‍💻 Developed By @PREMGUPTA2M"
            ),
            reply_markup=buttons
        )

    # =====================================================
    # MAIN START MESSAGE
    # =====================================================

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨ **PRIME CALCULATOR ACTIVATED** ✨\n\n"
            "⚡ Ultra Fast Response\n"
            "🧮 Professional Calculator\n"
            "👥 Group Working Enabled\n"
            "📢 Broadcast System Active\n"
            "🔒 Secure Force Join System\n\n"
            "👇 Use Calculator Buttons Below\n\n"
            "👨‍💻 Developed By @PREMGUPTA2M"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# VERIFY JOIN BUTTON
# =========================================================

@app.on_callback_query(filters.regex("verify_join"))
async def verify_join(client, query):

    user_id = query.from_user.id

    joined = await check_force_join(user_id)

    if not joined:

        return await query.answer(
            "❌ First Join Channel & Group",
            show_alert=True
        )

    await query.message.edit_caption(
        caption=(
            "✅ **Verification Successful**\n\n"
            "🧮 Prime Calculator Ready\n"
            "⚡ Enjoy Fast Calculator Service\n\n"
            "👨‍💻 Developed By @PREMGUPTA2M"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# CALLBACK CALCULATOR
# =========================================================

@app.on_callback_query()
async def callback_calculator(client, query):

    data = query.data

    if data == "verify_join":
        return

    user_id = query.from_user.id

    if user_id not in calculator_data:
        calculator_data[user_id] = ""

    expression = calculator_data[user_id]

    # =====================================================
    # CLEAR
    # =====================================================

    if data == "clear":

        expression = ""

    # =====================================================
    # RESULT
    # =====================================================

    elif data == "=":

        try:
            expression = str(eval(expression))
        except:
            expression = "Error"

    # =====================================================
    # ADD INPUT
    # =====================================================

    else:
        expression += data

    calculator_data[user_id] = expression

    try:

        await query.message.edit_caption(
            caption=(
                "🧮 **PRIME CALCULATOR**\n\n"
                f"`{expression}`\n\n"
                "⚡ Fast Calculation Active\n\n"
                "👨‍💻 Developed By @PREMGUPTA2M"
            ),
            reply_markup=calculator_buttons
        )

    except:
        pass

# =========================================================
# GROUP CALCULATOR SYSTEM
# =========================================================

@app.on_message(
    filters.text &
    ~filters.command(
        [
            "start",
            "broadcast",
            "gcast",
            "users",
            "help"
        ]
    )
)
async def auto_calculator(client, message):

    try:

        # SAVE GROUP
        if message.chat.type in ["group", "supergroup"]:
            save_group(message.chat.id)

        text = message.text.strip()

        allowed = "0123456789+-*/().% "

        for char in text:
            if char not in allowed:
                return

        result = eval(text)

        await message.reply_text(
            "🧮 **CALCULATION RESULT**\n\n"
            f"📥 Expression : `{text}`\n"
            f"📤 Result : `{result}`\n\n"
            "⚡ Powered By Prime Calculator"
        )

    except:
        pass

# =========================================================
# TOTAL USERS
# =========================================================

@app.on_message(
    filters.command("users") &
    filters.user(OWNER_ID)
)
async def total_users(client, message):

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()

    await message.reply_text(
        "📊 **PRIME CALCULATOR STATS**\n\n"
        f"👤 Total Users : `{len(users)}`\n"
        f"👥 Total Groups : `{len(groups)}`\n\n"
        "👨‍💻 Developed By @PREMGUPTA2M"
    )

# =========================================================
# USER BROADCAST
# =========================================================

@app.on_message(
    filters.command("broadcast") &
    filters.user(OWNER_ID)
)
async def broadcast_users(client, message):

    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply To Any Message"
        )

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    sent = 0
    failed = 0

    msg = await message.reply_text(
        "📢 Broadcasting To Users..."
    )

    for user in users:

        try:

            await message.reply_to_message.copy(
                int(user)
            )

            sent += 1

        except:
            failed += 1

    await msg.edit_text(
        "✅ USER BROADCAST COMPLETED\n\n"
        f"✔ Sent : `{sent}`\n"
        f"❌ Failed : `{failed}`"
    )

# =========================================================
# GROUP BROADCAST
# =========================================================

@app.on_message(
    filters.command("gcast") &
    filters.user(OWNER_ID)
)
async def group_broadcast(client, message):

    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply To Any Message"
        )

    with open(GROUPS_FILE, "r") as f:
        groups = f.read().splitlines()

    sent = 0
    failed = 0

    msg = await message.reply_text(
        "📢 Broadcasting To Groups..."
    )

    for group in groups:

        try:

            await message.reply_to_message.copy(
                int(group)
            )

            sent += 1

        except Exception as e:

            print(e)

            failed += 1

    await msg.edit_text(
        "✅ GROUP BROADCAST COMPLETED\n\n"
        f"✔ Sent : `{sent}`\n"
        f"❌ Failed : `{failed}`"
    )

# =========================================================
# HELP COMMAND
# =========================================================

@app.on_message(filters.command("help"))
async def help_command(client, message):

    await message.reply_text(
        "📚 **PRIME CALCULATOR HELP MENU**\n\n"
        "🧮 Send Any Math Expression\n"
        "`5+5`\n"
        "`100/2`\n"
        "`9*9`\n\n"
        "📢 Owner Commands:\n"
        "/users\n"
        "/broadcast\n"
        "/gcast\n\n"
        "👨‍💻 Developed By @PREMGUPTA2M"
    )

# =========================================================
# BOT STARTED
# =========================================================

print("✅ Prime Calculator Bot Started")

app.run()
