import discord
import os
from dotenv import load_dotenv
import json
import random
import math
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TRPG_PATH = os.getenv("TRPG_PATH")
CHARACTOR_PATH = os.getenv("CHARACTOR_PATH")

with open(TRPG_PATH, "r", encoding="utf-8") as f:
    trpg = json.load(f)

with open(CHARACTOR_PATH, "r", encoding="utf-8") as f:
    charactor = json.load(f)

skill_list = trpg.get("skills", [])
blacklists = trpg.get("blacklists", [])

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

def create_message_content(author, num_dice, num_sides, rolls, result, target=None, judge=None, operator=None, modifier=None ,skill=None):
    expr = f"{author}"

    if skill is not None:
        expr += f" ({skill})"

    expr += f" {num_dice}d{num_sides}"

    if operator:
        expr += f"\\{operator}{modifier}"

    if target is not None:
        expr += f" <= {target}"

    if num_dice == 1:
        detail = str(rolls[0])
    else:
        detail = f"{rolls} = {sum(rolls)}"

    if operator:
        detail += f"\\{operator}{modifier} \n--> {result}"

    if judge:
        detail += f" ({judge})"
    return f"{expr}\n--> {detail}"

def check_next_word(word):
    skill = None
    target = None

    if word.isdigit() or (word.startswith('-') and word[1:].isdigit()):
        target = int(word)
    elif word in skill_list:
        skill = word

    return skill, target

def parse(text, i):
    if text[i].lower() == "dd":
        if i + 1 < len(text):
            skill, target = check_next_word(text[i + 1])
            return skill, target, False
        return None, None, False

    m = re.fullmatch(rf"dd(-?\d+)", text[i])
    if m:
        return None, int(m.group(1)), False

    if text[i].lower() == "sdd":
        if i + 1 < len(text):
            skill, target = check_next_word(text[i + 1])
            return skill, target, True
        return None, None, True

    m = re.fullmatch(rf"sdd(-?\d+)", text[i])
    if m:
        return None, int(m.group(1)), True

    return None, None, False

def get_charactor(message):
    user_id = str(message.author.id)

    user_data = charactor["using_charactor"].get(user_id)

    if user_data is None:
        return None

    charactor_id = user_data["id"]
    return charactor_id


def get_skill_value(id, skill):
    character_data = charactor["charactor"].get(id)

    if character_data is None:
        return None

    skills = character_data.get("skills")

    if skills is None:
        return None

    return skills.get(skill)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id in blacklists:
        return

    if message.content.startswith('よぐぱんち'):
        author = message.author.mention
        skill = "よぐぱんち"
        num_dice, num_sides = 1, 3
        rolls, result = roll_dice(num_dice, num_sides)
        message_content = create_message_content(
            author, 
            num_dice, 
            num_sides, 
            rolls, 
            sum(rolls), 
            skill=skill)
        await message.channel.send(message_content)
        return

    if re.search(r"精神分析",message.content) and str(message.author.id) == "1529660407525019799":
        author = message.author.mention
        skill = "精神分析"
        num_dice, num_sides = 1, 100
        target = 95
        rolls, result = roll_dice(num_dice, num_sides)
        judge = judgement(result, target)

        message_content = create_message_content(
            author,
            num_dice,
            num_sides,
            rolls,
            sum(rolls),
            target,
            judge,
            skill=skill)
        
        await message.channel.send(message_content)
        return

    text = message.content.split()
    for i, t in enumerate(text):
        skill, target, secret= parse(text, i)
        if skill is not None or target is not None or t.lower() in ["dd", "sdd"]:
            num_dice, num_sides = 1, 100
            rolls, result = roll_dice(num_dice, num_sides)

            if skill is not None:
                charactor_id = get_charactor(message)
                if charactor_id is None:
                    await message.channel.send(f"{message.author.mention} キャラが登録されてないよ")
                else:
                    target = get_skill_value(charactor_id,skill)

            judge = None
            if target is not None:
                judge = judgement(result, target)

            message_content = create_message_content(
                message.author.mention,
                num_dice,
                num_sides,
                rolls,
                result,
                target,
                judge,
                skill=skill
            )

            if secret:
                if message.guild is not None:
                    await message.delete()
                    await message.channel.send("🎲secret dice(^^)🎲")
                await message.author.send(message_content)
            else:
                await message.channel.send(message_content)

        
client.run(TOKEN)