import pytz
from os import environ
from info import ADMINS, PREMIUM_LOGS
from datetime import datetime, timedelta
from pyrogram import Client, filters
from database.users_chats_db import db
import time
import asyncio
import logging

# Ensure logging is configured at the beginning of your script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def get_seconds(duration_str):
    duration_str = duration_str.lower()
    if "month" in duration_str:
        return int(duration_str.split()[0]) * 30 * 24 * 60 * 60
    elif "week" in duration_str:
        return int(duration_str.split()[0]) * 7 * 24 * 60 * 60
    elif "day" in duration_str:
        return int(duration_str.split()[0]) * 24 * 60 * 60
    elif "hour" in duration_str:
        return int(duration_str.split()[0]) * 60 * 60
    elif "minute" in duration_str:
        return int(duration_str.split()[0]) * 60
    return 0

@Client.on_message(filters.command("code") & filters.user(ADMINS))
async def generate_code_cmd(client, message):
    try:
        if len(message.command) == 3:
            duration_str = message.command[1] + " " + message.command[2]
            seconds = await get_seconds(duration_str)
            if seconds > 0:
                code = await db.generate_code(seconds)
                await message.reply_text(f"𝐁𝐨𝐭 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐂𝐨𝐝𝐞 ♻️\n\n⏰ Vᴀʟɪᴅɪᴛʏ: {duration_str}\n🎟️ Cᴏᴅᴇ: <code>{code}</code>\n\n𝐔𝐬𝐚𝐠𝐞 : <a href=https://t.me/c/2165249824/4>/redeem</a> xxxxxxxxxx\n\n𝐍𝐨𝐭𝐞 : Oɴʟʏ Oɴᴇ Usᴇʀ Cᴀɴ Usᴇ")
            else:
                await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴜsᴇ '<code>1 month</code>', '<code>1 week</code>', '<code>1 day</code>', '<code>1 minute</code>'.")
        else:
            await message.reply_text("Usage: /code <number> <time_unit> (e.g., /code 1 month)")
    except Exception as e:
        await message.reply(f"{e}")
        
@Client.on_message(filters.command("redeem"))
async def redeem_code_cmd(client, message):
    if len(message.command) == 2:
        code = message.command[1]
        user_id = message.from_user.id
        code_data = await db.codes.find_one({"code_hash": db.hash_code(code)})
        if not await db.has_premium_access(message.from_user.id):
            if code_data and not code_data['used'] and datetime.now() <= code_data['expiry_time']:
                # Update user data with new premium access expiry
                current_expiry = datetime.now()
                new_expiry = max(current_expiry, datetime.now()) + (code_data['expiry_time'] - datetime.now())
                user_data = {"id": user_id, "expiry_time": new_expiry}
                await db.update_user(user_data)
                await db.codes.update_one(
                    {"_id": code_data["_id"]},
                    {"$set": {"used": True, "user_id": user_id}}
                )
                expiry_str_in_ist = new_expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : %d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")
                await message.reply_text(f"🎉 ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!\nɴᴏᴡ ʜᴀᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴜɴᴛɪʟ\nᴠɪᴇᴡ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs /myplan\n\n<a href=https://t.me/c/2165249824/3>🔅 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇ 🔆</a>\n\n{expiry_str_in_ist}.")
                await client.send_message(chat_id=PREMIUM_LOGS, text=f"#𝐂𝐨𝐝𝐞_𝐑𝐞𝐝𝐞𝐞𝐦𝐞𝐝 ✅\n\n🎉 ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n👤 Usᴇʀ : {message.from_user.mention}\n\n🔅 <a href=https://t.me/c/2165249824/3>ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇ</a> 🔆\n\n{expiry_str_in_ist}")
            else:
                await message.reply_text("🚫ɪɴᴠᴀʟɪᴅ\n⏱️ ᴇxᴘɪʀᴇᴅ \n🙅 ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ ᴄᴏᴅᴇ.")
        else:
            await message.reply("#𝐀𝐥𝐫𝐞𝐚𝐝𝐲_𝐏𝐫𝐞𝐦𝐢𝐮𝐦 ❌\n\nʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ\n\nʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜᴇ ᴄᴏᴅᴇ")
    else:
        await message.reply_text("Exᴀᴍᴘʟᴇ 👇:\n\n<code>/redeem 7HC3BK32TO</code>")

