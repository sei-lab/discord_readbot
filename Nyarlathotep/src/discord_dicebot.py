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

    if message.content.startswith('dd'):
        # Extract the number of sides from the command
        try:
            target = int(message.content.split()[1])

            result = random.randint(1,100)
            judge = judgement(result, target)
            await message.channel.send(f'{message.author.mention} 1d100 \n --> {result} ({judge})')
        except (IndexError, ValueError):
            await message.channel.send("使い方: dd num")

    if re.fullmatch(r"(\d+)d(\d+)", message.content):
        # Extract the number of dice and sides from the command
        num_dice, num_sides = map(int, re.fullmatch(r"(\d+)d(\d+)", message.content).groups())
        if num_dice < 1 or num_sides < 1:
            await message.channel.send("そのダイスは振れないよ")
            return
        # Roll the dice
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls)
        await message.channel.send(f'{message.author.mention} {num_dice}d{num_sides} \n --> {rolls} --> {total}')

    if re.fullmatch(r"(\d+)b(\d+)", message.content):
        # Extract the number of dice and sides from the command
        num_dice, num_sides = map(int, re.fullmatch(r"(\d+)b(\d+)", message.content).groups())
        # Roll the dice
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        sort_rolls = sorted(rolls, reverse=False)
        await message.channel.send(f'{message.author.mention} {num_dice}b{num_sides} \n --> {sort_rolls}')

client.run(TOKEN)