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
    return "Prime Calculator Bot Running Successfully"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

# =========================================================
# TELEGRAM BOT CLIENT
# =========================================================

app = Client(
    "PrimeCalculatorBot",
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
GROUPS_FILE = "groups.txt"

if not os.path.exists(USERS_FILE):
    open(USERS_FILE, "w").close()

if not os.path.exists(GROUPS_FILE):
    open(GROUPS_FILE, "w").close()

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
# SAVE GROUP
# =========================================================

def save_group(group_id):

    with open(GROUPS_FILE, "r") as file:
        groups = file.read().splitlines()

    if str(group_id) not in groups:

        with open(GROUPS_FILE, "a") as file:
            file.write(f"{group_id}\n")

# =========================================================
# FORCE JOIN CHECK
# =========================================================

async def check_force_join(client, user_id):

    try:

        await client.get_chat_member(
            FORCE_CHANNEL,
            user_id
        )

    except:
        return False

    try:

        await client.get_chat_member(
            FORCE_GROUP,
            user_id
        )

    except:
        return False

    return True

# =========================================================
# PROFESSIONAL CALCULATOR BUTTONS
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

    joined = await check_force_join(
        client,
        user_id
    )

    # ================= FORCE JOIN ================= #

    if joined is False:

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
                "✨ **Welcome To Prime Calculator Bot**\n\n"
                "⚠️ To Continue,\n"
                "Please Join Our Official Channel & Group."
            ),
            reply_markup=buttons
        )

    # ================= MAIN MENU ================= #

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨ **Prime Calculator Activated**\n\n"
            "⚡ Fast Response\n"
            "🧮 Advanced Calculator\n"
            "👥 Group Support Enabled\n"
            "📢 Broadcast System Enabled\n\n"
            "👇 Use Buttons Below"
        ),
        reply_markup=calculator_buttons
    )

# =========================================================
# VERIFY JOIN BUTTON
# =========================================================

@app.on_callback_query(filters.regex("check_join"))
async def verify_join(client, callback_query):

    user_id = callback_query.from_user.id

    joined = await check_force_join(
        client,
        user_id
    )

    if joined is False:

        return await callback_query.answer(
            "❌ Join Channel & Group First",
            show_alert=True
        )

    await callback_query.message.edit_caption(
        caption=(
            "✅ **Verification Successful**\n\n"
            "🧮 Calculator Ready"
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
                "🧮 **Prime Calculator**\n\n"
                f"`{expression}`"
            ),
            reply_markup=calculator_buttons
        )

    except:
        pass

# =========================================================
# GROUP & PRIVATE CALCULATOR
# =========================================================

@app.on_message(
    filters.text &
    (filters.group | filters.private) &
    ~filters.command(
        ["start", "help", "broadcast", "gcast", "users"]
    )
)
async def text_calculator(client, message):

    try:

        if message.chat.type in ["group", "supergroup"]:
            save_group(message.chat.id)

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
# PRIVATE BROADCAST
# =========================================================

@app.on_message(
    filters.command("broadcast") &
    filters.user(OWNER_ID)
)
async def broadcast_users(client, message):

    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply To Message For Broadcast"
        )

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    success = 0
    failed = 0

    status = await message.reply_text(
        "📢 Broadcasting To Users..."
    )

    for user in users:

        try:

            await message.reply_to_message.copy(
                int(user)
            )

            success += 1

        except:

            failed += 1

    await status.edit_text(
        "✅ User Broadcast Completed\n\n"
        f"✔ Success : {success}\n"
        f"❌ Failed : {failed}"
    )

# =========================================================
# GROUP BROADCAST
# =========================================================

@app.on_message(
    filters.command("gcast") &
    filters.user(OWNER_ID)
)
async def broadcast_groups(client, message):

    if not message.reply_to_message:

        return await message.reply_text(
            "❌ Reply To Message For Group Broadcast"
        )

    with open(GROUPS_FILE, "r") as file:
        groups = file.read().splitlines()

    success = 0
    failed = 0

    status = await message.reply_text(
        "📢 Broadcasting To Groups..."
    )

    for group in groups:

        try:

            await message.reply_to_message.copy(
                int(group)
            )

            success += 1

        except:

            failed += 1

    await status.edit_text(
        "✅ Group Broadcast Completed\n\n"
        f"✔ Success : {success}\n"
        f"❌ Failed : {failed}"
    )

# =========================================================
# TOTAL USERS
# =========================================================

@app.on_message(
    filters.command("users") &
    filters.user(OWNER_ID)
)
async def total_users(client, message):

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    with open(GROUPS_FILE, "r") as file:
        groups = file.read().splitlines()

    await message.reply_text(
        "📊 **Prime Calculator Stats**\n\n"
        f"👤 Users : {len(users)}\n"
        f"👥 Groups : {len(groups)}"
    )

# =========================================================
# HELP COMMAND
# =========================================================

@app.on_message(filters.command("help"))
async def help_command(client, message):

    await message.reply_text(
        "📚 **Prime Calculator Commands**\n\n"
        "/start - Start Bot\n"
        "/help - Help Menu\n"
        "/users - Bot Stats\n"
        "/broadcast - User Broadcast\n"
        "/gcast - Group Broadcast\n\n"
        "🧮 Send Any Math Expression:\n"
        "`5+5`\n"
        "`100/2`\n"
        "`9*9`"
    )

# =========================================================
# BOT START
# =========================================================

print("Prime Calculator Bot Started Successfully")

app.run()
