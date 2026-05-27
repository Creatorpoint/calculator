from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
import os

app = Client(
    "CalculatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

users_file = "users.txt"

if not os.path.exists(users_file):
    open(users_file, "w").close()


def save_user(user_id):
    with open(users_file, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(users_file, "a") as f:
            f.write(f"{user_id}\n")


async def check_force_join(client, user_id):
    try:
        await client.get_chat_member(FORCE_CHANNEL, user_id)
        await client.get_chat_member(FORCE_GROUP, user_id)
        return True
    except:
        return False


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
            InlineKeyboardButton("-", callback_data="-")
        ],
        [
            InlineKeyboardButton("0", callback_data="0"),
            InlineKeyboardButton(".", callback_data="."),
            InlineKeyboardButton("=", callback_data="="),
            InlineKeyboardButton("+", callback_data="+")
        ],
        [
            InlineKeyboardButton("Clear", callback_data="clear")
        ]
    ]
)

user_data = {}


@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    save_user(user_id)

    joined = await check_force_join(client, user_id)

    START_IMAGE = "https://files.catbox.moe/splh4m.jpg"

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
                        "✅ Check Join",
                        callback_data="check_join"
                    )
                ]
            ]
        )

        return await message.reply_photo(
            photo=START_IMAGE,
            caption=(
                "✨ Welcome To Professional Calculator Bot

"
                "⚠️ To Use This Bot Please Join Our Official Channel & Group First."
            ),
            reply_markup=buttons
        )

    await message.reply_photo(
        photo=START_IMAGE,
        caption=(
            "✨Calculator Bot Ready

"
            "Use The Buttons Below 👇"
        ),
        reply_markup=calculator_buttons
    )


@app.on_callback_query(filters.regex("check_join"))
async def check_join_callback(client, callback_query):
    user_id = callback_query.from_user.id

    joined = await check_force_join(client, user_id)

    if not joined:
        return await callback_query.answer(
            "Join Channel & Group First",
            show_alert=True
        )

    await callback_query.message.edit_text(
        "✨ Access Granted\n\nCalculator Ready 👇",
        reply_markup=calculator_buttons
    )


@app.on_callback_query()
async def calculator(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "check_join":
        return

    if user_id not in user_data:
        user_data[user_id] = ""

    expression = user_data[user_id]

    if data == "clear":
        expression = ""

    elif data == "=":
        try:
            result = str(eval(expression))
            expression = result
        except:
            expression = "Error"

    else:
        expression += data

    user_data[user_id] = expression

    try:
        await callback_query.message.edit_text(
            f"```{expression}```",
            reply_markup=calculator_buttons
        )
    except:
        pass


@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply To Any Message To Broadcast"
        )

    with open(users_file, "r") as f:
        users = f.read().splitlines()

    success = 0
    failed = 0

    status = await message.reply_text("Broadcast Started...")

    for user in users:
        try:
            await message.reply_to_message.copy(int(user))
            success += 1
        except:
            failed += 1

    await status.edit_text(
        f"✅ Broadcast Completed\n\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )


@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_count(client, message):
    with open(users_file, "r") as f:
        users = f.read().splitlines()

    await message.reply_text(
        f"👥 Total Users: {len(users)}"
    )


print("Bot Started...")
app.run()
