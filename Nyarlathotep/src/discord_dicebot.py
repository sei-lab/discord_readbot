import discord
import os
from dotenv import load_dotenv
import random
import math
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def roll_dice(num_dice, num_sides):
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total = sum(rolls)
    return rolls, total

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

    if message.content.startswith('よぐぱんち'):
        num_dice, num_sides = 1, 100
        rolls, result = roll_dice(num_dice, num_sides)
        await message.channel.send(f'{message.author.mention} {num_dice}d{num_sides} \n --> {result}')

    if re.search(r"精神分析",message.content) and str(message.author.id) == "1529660407525019799":
        rolls, result = roll_dice(1, 100)
        judge = judgement(result, 95)
        await message.channel.send(f'{message.author.mention} 精神分析 1d100 \n --> {result} ({judge})')

    text = message.content.split()
    for i, t in enumerate(text):
        if t.lower() == "dd":
            rolls, result = roll_dice(1, 100)
            if i + 1 < len(text) and text[i+1].isdigit():
                target = int(text[i+1])
                judge = judgement(result, target)
                await message.channel.send(f'{message.author.mention} 1d100 \n --> {result} ({judge})')
            else:
                await message.channel.send(f'{message.author.mention} 1d100 \n --> {result}')
            return
        m = re.fullmatch(r"(\d+)[dD](\d+)(?:([+\-*/^])(\d+))?", t)
        if m:
            num_dice = int(m.group(1))
            num_sides = int(m.group(2))
            operator = m.group(3)
            modifier = int(m.group(4)) if m.group(4) else None

            if num_dice <= 0 or num_sides <= 0:
                await message.channel.send(f"{message.author.mention} そのダイスは振れないよ(^^)")
                return
            elif num_dice * num_sides > 10000000 or (operator == "^" and modifier and num_dice * num_sides * modifier > 1000000000):
                await message.channel.send(f"{message.author.mention} ちょちょちょ多すぎるって...(^^)")
                return
            if operator == "/" and modifier == 0:
                await message.channel.send("0では割れないよ(^^)")
                return

            # 通常のダイス
            if operator != "^":
                rolls, total = roll_dice(num_dice, num_sides)

                if operator == "+":
                    total += modifier
                elif operator == "-":
                    total -= modifier
                elif operator == "*":
                    total *= modifier
                elif operator == "/":
                    total //= modifier

                expr = f"{num_dice}d{num_sides}"
                if operator:
                    expr += f"\\{operator}{modifier}"

                if num_dice == 1:
                    detail = str(rolls[0])
                else:
                    detail = f"{rolls} = {sum(rolls)}"

                if operator:
                    detail += f"\\{operator}{modifier} \n--> {total}"

                await message.channel.send(
                    f"{message.author.mention} {expr}\n--> {detail}"
                )

            # ^ の特殊処理
            else:
                totals = []

                for _ in range(modifier):
                    _, total = roll_dice(num_dice, num_sides)
                    totals.append(total)

                result = math.prod(totals)

                await message.channel.send(
                    f"{message.author.mention} "
                    f"{num_dice}d{num_sides}^{modifier}\n"
                    f"--> {totals}^{modifier}\n"
                    f"--> {result}"
                )
            return

client.run(TOKEN)