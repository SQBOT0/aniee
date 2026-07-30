from pyrogram import Client, filters
from pyrogram.types import Message
import os
import math
import time

from ANIYAXMUSIC import app


MAX_SIZE = 5 * 1024 * 1024 * 1024  # 5GB


def parse_split(value):

    value = value.lower().strip()

    if value.endswith("kb"):
        return "size", int(float(value[:-2]) * 1024)

    elif value.endswith("mb"):
        return "size", int(float(value[:-2]) * 1024 * 1024)

    elif value.endswith("gb"):
        size = int(float(value[:-2]) * 1024 * 1024 * 1024)

        if size > MAX_SIZE:
            raise ValueError("Maximum 5GB allowed")

        return "size", size


    elif "line" in value:

        number = (
            value
            .replace("lines", "")
            .replace("line", "")
            .strip()
        )

        if not number.isdigit():
            raise ValueError("Invalid line")

        return "line", int(number)


    else:
        raise ValueError("Invalid format")



def file_report(file_path):

    data = {}

    size = os.path.getsize(file_path)

    data["size"] = round(
        size / (1024 * 1024),
        2
    )


    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        lines = f.readlines()


    data["total"] = len(lines)

    data["empty"] = sum(
        1 for x in lines
        if not x.strip()
    )


    clean = [
        x.strip()
        for x in lines
        if x.strip()
    ]


    data["duplicate"] = (
        len(clean)
        -
        len(set(clean))
    )


    data["unique"] = len(
        set(clean)
    )


    return data



@app.on_message(filters.command("sbsplit") & filters.reply)
async def split_file(client: Client, message: Message):

    start_time = time.time()

    replied = message.reply_to_message


    if not replied or not replied.document:
        return await message.reply_text(
            "Reply to TXT file.\n\n"
            "Examples:\n"
            "/sbsplit 10mb\n"
            "/sbsplit 2gb\n"
            "/sbsplit 100line"
        )


    if not replied.document.file_name.lower().endswith(".txt"):
        return await message.reply_text(
            "Only TXT files supported."
        )


    if len(message.command) < 2:
        return await message.reply_text(
            "Example: /sbsplit 10mb"
        )


    try:
        split_type, value = parse_split(
            message.command[1]
        )

    except:
        return await message.reply_text(
            "Invalid format."
        )



    msg = await message.reply_text(
        "Downloading..."
    )


    file_path = await client.download_media(
        replied.document
    )


    if not file_path:
        return await msg.edit(
            "Download failed."
        )


    info = file_report(file_path)


    await msg.edit(
        f"📄 File Report\n\n"
        f"Name: {replied.document.file_name}\n"
        f"Size: {info['size']} MB\n\n"
        f"Total Lines: {info['total']}\n"
        f"Empty Lines: {info['empty']}\n"
        f"Duplicate Lines: {info['duplicate']}\n"
        f"Unique Lines: {info['unique']}\n\n"
        f"Starting split..."
    )


    base_name = os.path.splitext(
        replied.document.file_name
    )[0]


    total_parts = 0


    try:


        if split_type == "size":

            total_size = os.path.getsize(
                file_path
            )

            total_parts = math.ceil(
                total_size / value
            )


            with open(
                file_path,
                "rb"
            ) as f:


                for i in range(total_parts):

                    part_file = (
                        f"{base_name}_part{i+1}.txt"
                    )


                    with open(
                        part_file,
                        "wb"
                    ) as out:

                        out.write(
                            f.read(value)
                        )
                        await client.send_document(
                        message.chat.id,
                        part_file,
                        caption=(
                            f"Part {i+1}/{total_parts}"
                        )
                    )


                    os.remove(part_file)



        elif split_type == "line":


            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                lines = f.readlines()



            total_parts = math.ceil(
                len(lines) / value
            )



            for i in range(total_parts):

                part_file = (
                    f"{base_name}_part{i+1}.txt"
                )


                start = i * value
                end = start + value


                with open(
                    part_file,
                    "w",
                    encoding="utf-8"
                ) as out:

                    out.writelines(
                        lines[start:end]
                    )


                await client.send_document(
                    message.chat.id,
                    part_file,
                    caption=(
                        f"Part {i+1}/{total_parts}\n"
                        f"Lines {start+1}-{min(end,len(lines))}"
                    )
                )


                os.remove(part_file)



        finish = round(
            time.time() - start_time,
            2
        )


        await message.reply_text(
            f"✅ Split Completed\n\n"
            f"Parts: {total_parts}\n"
            f"Time: {finish} sec"
        )


    finally:

        if os.path.exists(file_path):
            os.remove(file_path)
            
