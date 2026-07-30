import os
import shutil
import patoolib
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


def extract_archive(archive_path):
    cleanup()

    os.makedirs(TEMP_DIR, exist_ok=True)

    patoolib.extract_archive(
        archive_path,
        outdir=TEMP_DIR
    )


def create_txt():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:

                path = os.path.join(root, file)

                out.write("\n" + "=" * 70 + "\n")
                out.write(f"FILE : {os.path.relpath(path, TEMP_DIR)}\n")
                out.write("=" * 70 + "\n\n")

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        out.write(f.read())
                except Exception:
                    out.write("[Binary File - Cannot Display]\n")

                out.write("\n\n")


@app.on_message(filters.reply & filters.command("txt"))
async def archive_to_txt(client: Client, message: Message):

    replied = message.reply_to_message

    if not replied:
        return await message.reply_text("❌ Reply to an archive file.")

    if not replied.document:
        return await message.reply_text("❌ Reply to a ZIP/RAR/7Z archive.")

    file_name = replied.document.file_name.lower()

    allowed = (
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".tgz",
        ".bz2",
        ".xz"
    )

    if not file_name.endswith(allowed):
        return await message.reply_text(
            "❌ Supported formats:\n\nZIP\nRAR\n7Z\nTAR\nTGZ\nGZ\nBZ2\nXZ"
        )

    status = await message.reply_text("📥 Downloading archive...")

    archive_path = await replied.download()

    try:
        await status.edit("📂 Extracting archive...")

        extract_archive(archive_path)

        await status.edit("📝 Creating TXT...")

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

        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error:\n`{e}`")

    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)

        cleanup()
