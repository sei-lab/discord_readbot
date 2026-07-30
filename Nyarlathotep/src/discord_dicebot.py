import discord
import os
from dotenv import load_dotenv
import random

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

client.run(TOKEN)