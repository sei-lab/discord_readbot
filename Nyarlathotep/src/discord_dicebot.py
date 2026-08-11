import discord
import os
from dotenv import load_dotenv
import json
import random
import math
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

skill_file_path = "../data/dice_data.json"
with open(skill_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

skill_list = data.get("skills", [])
blacklist = data.get("blacklist", [])

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def roll_dice(num_dice, num_sides):
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total = sum(rolls)
    return rolls, total

def judgement(result, target):
    if target <= 0:
        return "ファンブル"
    if result <= 5:
        return "クリティカル"
    elif result <= target // 5:
        return "エクストリーム成功"
    elif result <= target // 2:
        return "ハード成功"
    elif result <= target:
        return "成功"
    elif result >= 95:
        return "ファンブル"
    else:
        return "失敗"

def create_message_content(author, skill=None, num_dice, num_sides, rolls, total, result, judge=None, operator=None, modifier=None):
    expr = f"{author}"

    if skill is not None:
        expr += f" ({skill})"

    expr += f" {num_dice}d{num_sides}"

    if operator:
        expr += f"\\{operator}{modifier}"

    if num_dice == 1:
        detail = str(rolls[0])
    else:
        detail = f"{rolls} = {total}"

    if operator:
        detail += f"\\{operator}{modifier} \n--> {result}"

    if judge:
        detail += f" ({judge})"
    return f"{expr}\n--> {detail}"

def chack_next_word(word):
    skill = None
    target = None

    if word.isdigit() or (word.startswith('-') and word[1:].isdigit()):
        target = int(word)
    elif word in skill_list:
        skill = word

    return skill, target

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author in blacklist:
        return

    if message.content.startswith('よぐぱんち'):
        author = message.author.mention
        num_dice, num_sides = 1, 3
        rolls, result = roll_dice(num_dice, num_sides)
        message_content = create_message_content(author, None, num_dice, num_sides, rolls, sum(rolls), result)
        await message.channel.send(message_content)

    if re.search(r"精神分析",message.content) and str(message.author.id) == "1529660407525019799":
        author = message.author.mention
        skill = "精神分析"
        rolls, result = roll_dice(1, 100)
        judge = judgement(result, 95)
        message_content = create_message_content(author, skill, 1, 100, rolls, sum(rolls), result, judge)
        await message.channel.send(message_content)

    text = message.content.split()
    for i, t in enumerate(text):
        if t.lower() == "dd":
            rolls, result = roll_dice(1, 100)
            if i + 1 < len(text):
                skill ,target = chack_next_word(text[i+1])
                if target is not None:
                    judge = judgement(result, target)
                    message_content = create_message_content(message.author.mention, skill, 1, 100, rolls, sum(rolls), result, judge) 
                else:
                    message_content = create_message_content(message.author.mention, skill, 1, 100, rolls, sum(rolls), result)
                message_content = create_message_content(message.author.mention, None, 1, 100, rolls, sum(rolls), result, judge)
            else:
                message_content = create_message_content(message.author.mention, None, 1, 100, rolls, sum(rolls), result, None)
            await message.channel.send(message_content)
        m = re.fullmatch(r"dd(\d+)",t)
        if m and (m.group(1).isdigit() or (m.group(1).startswith('-') and m.group(1)[1:].isdigit())):
            target = int(m.group(1))
            rolls, result = roll_dice(1, 100)
            judge = judgement(result, target)
            message_content = create_message_content(message.author.mention, None, 1, 100, rolls, sum(rolls), result, judge)
            await message.channel.send(message_content)
        
        m = re.fullmatch(r"(\d+)[dD](\d+)(?:([+\-*/^])(\d+))?", t)
        if m:
            num_dice = int(m.group(1))
            num_sides = int(m.group(2))
            operator = m.group(3)
            modifier = int(m.group(4)) if m.group(4) else None

            if num_dice <= 0 or num_sides <= 0:
                await message.channel.send(f"{message.author.mention} そのダイスは振れないよ(^^)")
                return
            elif num_dice * num_sides > 1000000000 or (operator == "^" and modifier and num_dice * num_sides * modifier > 1000000000):
                await message.channel.send(f"{message.author.mention} ちょちょちょ多すぎるって...(^^)")
                return
            elif operator == "/" and modifier == 0:
                await message.channel.send("0では割れないよ(^^)")
                return
            digits = len(str(num_sides))
            estimated = num_dice * (digits + 2) + 100  # メンションなどの余裕
            if estimated > 1900:
                await message.channel.send(
                f"{message.author.mention} 出力が長すぎるよ...(^^)"
                )
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

client.run(TOKEN)