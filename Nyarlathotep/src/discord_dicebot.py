import discord
import os
from dotenv import load_dotenv
import random
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

intents.message_content = True

def roll_dice(num_dice, num_sides):
    if num_dice == 1:
        rolls = random.randint(1, num_sides)
    else:
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    return rolls

def judgement(result, target):
    if result <= 5:
        return "クリティカル"
    elif result <= target // 5:
        return "エクストリーム成功"
    elif result < target // 2:
        return "ハード成功"
    elif result <= target:
        return "成功"
    elif result >= 95:
        return "ファンブル"
    else:
        return "失敗"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("dd"):
        parts = message.content.split()

        result = roll_dice(1, 100)  # Roll a single d100

        if len(parts) == 1:
            await message.channel.send(
                f"{message.author.mention} 1d100\n--> {result}")

        elif len(parts) == 2:
            # dd 85
            try:
                target = int(parts[1])
                judge = judgement(result, target)

                await message.channel.send(
                    f"{message.author.mention} 1d100\n--> {result} ({judge})"
                )
            except ValueError:
                await message.channel.send("使い方: dd または dd num")

        else:
            await message.channel.send("使い方: dd または dd num")

    if re.fullmatch(r"(\d+)d(\d+)", message.content):
        # Extract the number of dice and sides from the command
        num_dice, num_sides = map(int, re.fullmatch(r"(\d+)d(\d+)", message.content).groups())
        if num_dice < 1 or num_sides < 1:
            await message.channel.send("そのダイスは振れないよ(^^;)")
            return
        elif num_dice > 100 or (num_dice * num_sides) > 100000:
            await message.channel.send("ちょちょちょ多すぎるよ(^^;)")
            return

        rolls = roll_dice(num_dice, num_sides)
        if num_dice == 1:
            await message.channel.send(f'{message.author.mention} {num_dice}d{num_sides} \n --> {rolls}')
        else:
            total = sum(rolls)
            await message.channel.send(f'{message.author.mention} {num_dice}d{num_sides} \n --> {rolls} --> {total}')

    if re.fullmatch(r"(\d+)b(\d+)", message.content):
        # Extract the number of dice and sides from the command
        num_dice, num_sides = map(int, re.fullmatch(r"(\d+)b(\d+)", message.content).groups())
        if num_dice < 1 or num_sides < 1:
            await message.channel.send("そのダイスは振れないよ(^^;)")
            return
        elif num_dice > 100 or (num_dice * num_sides) > 100000:
            await message.channel.send("ちょちょちょ多すぎるよ(^^;)")
            return

        rolls = roll_dice(num_dice, num_sides)
        sort_rolls = sorted(rolls, reverse=False)
        await message.channel.send(f'{message.author.mention} {num_dice}b{num_sides} \n --> {sort_rolls}')

    if message.content.startswith('よぐぱんち'):
        num_dice, num_sides = 1,3
        rolls = roll_dice(num_dice, num_sides)
        await message.channel.send(f'{message.author.mention} {num_dice}d{num_sides} \n --> {rolls}')

    if re.search(r"精神分析",message.content) and str(message.author.id) == "1529660407525019799":
        result = random.randint(1,100)
        judge = judgement(result, 95)
        await message.channel.send(f'{message.author.mention} 精神分析 1d100 \n --> {result} ({judge})')

client.run(TOKEN)