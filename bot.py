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

app.run()
