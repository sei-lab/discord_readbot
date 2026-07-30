import discord
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

DISCORD_EPOCH = datetime(
    2015, 1, 1,
    tzinfo=ZoneInfo("UTC")
)

output_dir ="../output"
asset_dir = os.path.join( output_dir, "assets")

def select_guild(guilds):
    print("=== Servers ===")
    for i, guild in enumerate(guilds):
        print(f"{i}. {guild.name}")

    while True:
        user_input = input("Select a server by number (or type 'exit' to quit): ").strip()

        if user_input.lower() == "exit":
            print("Exiting the program.")
            return None

        try:
            choice = int(user_input)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice < 0 or choice >= len(guilds):
            print("Invalid choice. Please select a number from the list.")
            continue

        return guilds[choice]

async def get_channel_list(guild):
    targets = []

    for channel in guild.text_channels:
        targets.append({
        "name": channel.name,
        "type": "channel",
        "parent": None,
        "obj": channel
        })

        for thread in channel.threads:
            targets.append({
            "name": thread.name,
            "type": "thread",
            "parent": channel,
            "obj": thread
            })

        async for thread in channel.archived_threads(limit=None):
            targets.append({
            "name": thread.name,
            "type": "archived_thread",
            "parent": channel,
            "obj": thread
            })

    return targets

def select_target(targets):
    print("=== Targets ===")
    for i, target in enumerate(targets):
        if target["type"] == "channel":
            print(f"{i}. 📁 {target['name']}")
        elif target["type"] == "thread":
            print(f"{i}.   └ 💬 {target['name']}")
        else:
            print(f"{i}.   └ 📦 {target['name']} (Archived)")

    while True:
        user_input = input("Select a target by number (or type 'exit' to quit): ").strip()

        if user_input.lower() == "exit":
            print("Exiting the program.")
            return None

        try:
            choice = int(user_input)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice < 0 or choice >= len(targets):
            print("Invalid choice. Please select a number from the list.")
            continue

        return targets[choice]

async def get_messages(target, limit=None, after=None, before=None):
    messages = []

    async for message in target["obj"].history(
        limit=limit,
        after=after,
        before=before,
        oldest_first=True
    ):
        messages.append(message)

    return messages

def input_date_range():
    while True:
        after_input = input("Enter the start date (YYYY-MM-DD) or leave blank for no start date: ").strip()
        before_input = input("Enter the end date (YYYY-MM-DD) or leave blank for no end date: ").strip()

        after = None
        before = None

        if after is not None and after < DISCORD_EPOCH:
            print("開始日時は2015-01-01以降を指定してください。")
            continue

        if after_input:
            try:
                after = datetime.strptime(after_input, "%Y-%m-%d").replace(tzinfo=ZoneInfo("UTC"))
            except ValueError:
                print("Invalid start date format. Please use YYYY-MM-DD.")
                continue

        if before_input:
            try:
                before = datetime.strptime(before_input, "%Y-%m-%d").replace(tzinfo=ZoneInfo("UTC"))
            except ValueError:
                print("Invalid end date format. Please use YYYY-MM-DD.")
                continue

        return after, before

async def save_markdown(messages, target):

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(asset_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"{target['name']}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {target['name']}\n\n")

        for message in messages:

            # ------------------
            # 基本情報
            # ------------------
            timestamp = message.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S")

            f.write("---\n\n")
            f.write(f"## {message.author.display_name}\n")
            f.write(f"> {timestamp}\n\n")

            # ------------------
            # 返信
            # ------------------
            if message.reference:
                replied = message.reference.resolved

                if replied is None and message.reference.message_id:
                    try:
                        replied = await message.channel.fetch_message(
                            message.reference.message_id
                        )
                    except (discord.NotFound, discord.Forbidden):
                        replied = None

                if isinstance(replied, discord.Message):
                    preview = replied.content.replace("\n", " ")

                    if len(preview) > 80:
                        preview = preview[:80] + "..."

                    f.write("> **返信先**\n")
                    f.write(f"> {replied.author.display_name}: {preview}\n\n")

                elif replied is not None:
                    f.write("> **返信先:** *(元メッセージは削除されています)*\n\n")
            # ------------------
            # 本文
            # ------------------
            if message.content:
                f.write(message.content)
                f.write("\n\n")

            # ------------------
            # 添付ファイル
            # ------------------
            if message.attachments:
                f.write("### 添付ファイル\n")

                for attachment in message.attachments:
                    save_path = os.path.join(asset_dir, attachment.filename)

                    # 保存
                    await attachment.save(save_path)

                    # Obsidian用リンク
                    if attachment.content_type and attachment.content_type.startswith("image/"):
                        f.write(f"![[assets/{attachment.filename}]]\n")
                    else:
                        f.write(f"[[assets/{attachment.filename}]]\n")

                f.write("\n")

            # ------------------
            # スタンプ
            # ------------------
            if message.stickers:
                f.write("**スタンプ:** ")

                f.write(
                    ", ".join(sticker.name for sticker in message.stickers)
                )

                f.write("\n\n")

            # ------------------
            # リアクション
            # ------------------
            if message.reactions:
                reacts = []

                for reaction in message.reactions:
                    reacts.append(
                        f"{reaction.emoji} ×{reaction.count}"
                    )

                f.write("**リアクション:** ")
                f.write(" ".join(reacts))
                f.write("\n\n")

            if message.author.bot and message.embeds:
                for embed in message.embeds:
                    data = embed.to_dict()

                    f.write("### 🎲 ダイス結果\n\n")

                    if "author" in data:
                        f.write(f"**{data['author']['name']}**\n\n")

                    if "fields" in data:
                        for field in data["fields"]:
                            f.write(f"- **{field['name']}** {field['value']}\n")

                    f.write("\n")

            if not message.author.bot and message.embeds:
                f.write("### 埋め込み\n")

                for embed in message.embeds:
                    f.write(f"**タイトル:** {embed.title}\n")
                    f.write(f"**説明:** {embed.description}\n")
                    f.write(f"**URL:** {embed.url}\n\n")

@client.event
async def on_ready():

    guild = select_guild(client.guilds)

    print(f"server: {guild.name}")
    print()

    channels = await get_channel_list(guild)
    target = select_target(channels)
    if target is None:
        await client.close()
        return

    print(f"selected: {target['name']}")

    after, before = input_date_range()

    messages = await get_messages(
        target,
        limit=None,
        after=after,
        before=before
    )

    await save_markdown(messages, target)
    await client.close()  # 終了するためにクライアントを停止

client.run(TOKEN)