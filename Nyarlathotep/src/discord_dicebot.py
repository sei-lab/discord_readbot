import discord
import os
import csv
import io
import asyncio
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

def create_message_content(author, num_dice, num_sides, rolls, result, name=None, target=None, judge=None, operator=None, modifier=None ,skill=None):
    expr = f"{author}"

    if name is not None:
        expr += f" {name}"

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

def get_skill_value(charactor_id, skill):
    character_data = charactor["charactor"].get(charactor_id)

    if character_data is None:
        return None

    skills = character_data.get("skills")

    if skills is None:
        return None

    return skills.get(skill)

def generate_charactor_id():
    """既存のキャラクターIDから次のIDを生成する"""

    max_id = 0

    for charactor_id in charactor["charactor"]:
        m = re.fullmatch(r"C-(\d+)", charactor_id)

        if m:
            number = int(m.group(1))
            max_id = max(max_id, number)

    return f"C-{max_id + 1:04d}"


def save_charactor_data():
    """現在のcharactorデータをJSONに保存する"""

    with open(CHARACTOR_PATH, "w", encoding="utf-8") as f:
        json.dump(
            charactor,
            f,
            ensure_ascii=False,
            indent=4
        )


async def register_charactor(message, attachment):
    """Discordに添付されたCSVからキャラクターを登録する"""

    # CSVを読み込む
    file_data = await attachment.read()

    try:
        csv_text = file_data.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = file_data.decode("cp932")
        except UnicodeDecodeError:
            return None, "CSVを読み込めなかったよ"

    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    name = None

    for row in rows:
        if len(row) >= 2 and row[0] == "NAME":
            name = row[1].strip()
            break

    if not name:
        return None, "キャラクター名(NAME)が見つからないよ"



    for charactor_id, character_data in charactor["charactor"].items():
        if character_data.get("name") == name:
            return None, f"「{name}」はすでに登録されているよ（{charactor_id}）"

    status = {}

    ability_names = [
        "SAN",
        "LUCK",
        "HP",
        "MP",
        "MOV",
        "STR",
        "CON",
        "POW",
        "DEX",
        "APP",
        "SIZ",
        "INT",
        "EDU"
    ]

    for row in rows:
        if len(row) < 5:
            continue

        if row[0] not in ability_names:
            continue

        value = row[4].strip()

        if not value:
            continue

        try:
            status[row[0]] = int(value)
        except ValueError:
            pass

    if "HP" in status:
        status["MAX_HP"] = status["HP"]


    skills = {}

    skill_start = None

    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == "技能名":
            skill_start = i + 1
            break

    if skill_start is not None:

        for row in rows[skill_start:]:

            # 別セクションに入ったら終了
            if len(row) > 0 and row[0] in [
                "戦闘",
                "武器",
                "項目",
                "装備品と所持品",
                "収入と財産"
            ]:
                break

            # 技能名 + RGまで存在する必要がある
            if len(row) < 6:
                continue

            skill_name = row[0].strip()
            skill_value = row[5].strip()

            # 空行や無名技能を無視
            if not skill_name:
                continue

            if not skill_value:
                continue

            try:
                skills[skill_name] = int(skill_value)
            except ValueError:
                continue

    charactor_id = generate_charactor_id()

    charactor["charactor"][charactor_id] = {
        "name": name,
        "skills": {
            **status,
            **skills
        }
    }

    user_id = str(message.author.id)

    charactor["using_charactor"][user_id] = {
        "id": charactor_id,
        "name": name
    }

    save_charactor_data()

    return charactor_id, name

def delete_charactor(charactor_id):
    # キャラクターが存在するか確認
    if charactor_id not in charactor["charactor"]:
        return False, "そのキャラクターは登録されてないよ"

    name = charactor["charactor"][charactor_id]["name"]

    # キャラクター本体を削除
    del charactor["charactor"][charactor_id]

    # 使用キャラとして設定されているユーザーからも削除
    deleted_users = []

    for user_id, using_data in list(charactor["using_charactor"].items()):
        if using_data.get("id") == charactor_id:
            del charactor["using_charactor"][user_id]
            deleted_users.append(user_id)

    # JSONに保存
    save_charactor_data()

    return True, name

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

    # if message.content.startswith('SANC'):
    #     author = message.author.mention
    #     skill = "SAN"
    #     charactor_id = get_charactor(message)
    #     if charactor_id is not None:
    #         name = charactor["charactor"][charactor_id]["name"]
    #         target = get_skill_value(charactor_id,skill)
    #         num_dice, num_sides = 1, 100
    #         rolls, result = roll_dice(num_dice, num_sides)
    #         judge = judgement(result,target)
    #         message_content = create_message_content(
    #             author, 
    #             num_dice, 
    #             num_sides, 
    #             rolls, 
    #             sum(rolls), 
    #             target=target,
    #             judge=judge,
    #             name=name,
    #             skill=skill)
    #         await message.channel.send(message_content)

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
            target=target,
            judge=judge,
            name="よぐ=そとーす",
            skill=skill)
        
        await message.channel.send(message_content)
        return

    if message.content.startswith("!db update_charactor_sheet") \
        or message.content.strip().lower() == "!db ucs":

        if not message.attachments:
            await message.channel.send(
                f"{message.author.mention} CSVを添付してね"
            )
            return

        attachment = message.attachments[0]

        if not attachment.filename.lower().endswith(".csv"):
            await message.channel.send(
                f"{message.author.mention} CSVファイルを添付してね"
            )
            return

        charactor_id, name = await register_charactor(
            message,
            attachment
        )

        if charactor_id is None:
            await message.channel.send(
                f"{message.author.mention} {name}"
            )
            return

        await message.channel.send(
            f"{message.author.mention} "
            f"「{name}」を {charactor_id} として登録したよ(^^)"
        )

        return

    if message.content.startswith("!db delete_charactor_sheet") \
            or message.content.startswith("!db dcs"):

        text = message.content.split()

        if len(text) < 3:
            await message.channel.send(
                f"{message.author.mention} 削除するキャラクターIDを指定してね\n"
                f"例: `!db dcs C-0001`"
            )
            return

        charactor_id = text[2]

        # キャラクターの存在確認
        character_data = charactor["charactor"].get(charactor_id)

        if character_data is None:
            await message.channel.send(
                f"{message.author.mention} "
                f"{charactor_id} は登録されてないよ"
            )
            return

        name = character_data.get("name", "名前不明")

        # 確認メッセージ
        await message.channel.send(
            f"{message.author.mention}\n"
            f"本当に「{name}」({charactor_id})を削除する？\n"
            f"削除するならキャラクターの名前を入力してね。\n"
            f"10秒以内に答えてね。"
        )

        def check(reply):
            return (
                reply.author == message.author
                and reply.channel == message.channel
                and reply.content.lower() == f"{name}"
            )

        try:
            await client.wait_for(
                "message",
                timeout=10.0,
                check=check
            )

        except asyncio.TimeoutError:
            await message.channel.send(
                f"{message.author.mention} 時間切れ。削除しなかったよ。"
            )
            return

        # 実際に削除
        success, result = delete_charactor(charactor_id)

        if not success:
            await message.channel.send(
                f"{message.author.mention} {result}"
            )
            return

        await message.channel.send(
            f"{message.author.mention} "
            f"「{result}」({charactor_id})を削除したよ。"
        )

        return

    text = message.content.split()
    for i, t in enumerate(text):
        skill, target, secret= parse(text, i)
        if skill is not None or target is not None or t.lower() in ["dd", "sdd"]:
            num_dice, num_sides = 1, 100
            rolls, result = roll_dice(num_dice, num_sides)
            name = None

            if skill is not None:
                charactor_id = get_charactor(message)
                if charactor_id is None:
                    await message.channel.send(f"{message.author.mention} キャラが登録されてないよ")
                    skill = None
                else:
                    name = charactor["charactor"][charactor_id]["name"]
                    target = get_skill_value(charactor_id,skill)
                    if target is None:
                        await message.channel.send(f"{message.author.mention} {name}にその技能はないよ")
                        skill, name = None, None                    

            judge = None
            if target is not None:
                judge = judgement(result, target)

            message_content = create_message_content(
                message.author.mention,
                num_dice,
                num_sides,
                rolls,
                result,
                target=target,
                judge=judge,
                name=name,
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