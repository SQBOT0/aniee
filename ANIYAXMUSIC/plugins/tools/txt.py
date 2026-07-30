import os
import shutil
import zipfile
from pyrogram import Client, filters
from pyrogram.types import Message
from ANIYAXMUSIC import app

TEMP_DIR = "temp_extract"
OUTPUT_FILE = "messages.txt"


def cleanup():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)


def extract_zip(zip_path):
    cleanup()

    os.makedirs(TEMP_DIR, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(TEMP_DIR)


def create_txt():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for root, _, files in os.walk(TEMP_DIR):
            for file in files:

                path = os.path.join(root, file)

                out.write("=" * 70 + "\n")
                out.write(f"FILE : {os.path.relpath(path, TEMP_DIR)}\n")
                out.write("=" * 70 + "\n\n")

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        out.write(f.read())
                except Exception:
                    out.write("[Binary File - Cannot Display]")

                out.write("\n\n")


@app.on_message(filters.reply & filters.command("txt"))
async def archive_to_txt(client: Client, message: Message):

    replied = message.reply_to_message

    if not replied:
        return await message.reply_text("❌ Reply to a ZIP file.")

    if not replied.document:
        return await message.reply_text("❌ Reply to a ZIP file.")

    if not replied.document.file_name.lower().endswith(".zip"):
        return await message.reply_text("❌ Only ZIP files are supported.")

    archive_path = await replied.download()

    try:
        await message.reply_text("📥 Processing ZIP...")

        extract_zip(archive_path)

        create_txt()

        sender = message.from_user.first_name or "Unknown"

        if message.from_user.last_name:
            sender += f" {message.from_user.last_name}"

        caption = (
            "┏━━━━━━━⍟\n"
            "┃ 𝗛𝗲𝗿𝗲 𝗶𝘀 𝘆𝗼𝘂𝗿 .𝘁𝘅𝘁 𝗳𝗶𝗹𝗲 ✅\n"
            "┗━━━━━━━━━━━━━━━⊛\n"
            f"⊙ 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐛𝐲 :- {sender}"
        )

        await message.reply_document(
            OUTPUT_FILE,
            caption=caption
        )

    except zipfile.BadZipFile:
        await message.reply_text("❌ Invalid ZIP file.")

    except Exception as e:
        await message.reply_text(f"❌ Error:\n`{e}`")

    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)

        cleanup()
