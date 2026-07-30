import discord
import os
from dotenv import load_dotenv
import re
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     channel = client.get_channel(1532005786883063858)  # Replace with your channel ID
#     await channel.send("よぐ=そとーす参上！")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # blacklist = ["929754310475124796",""] 
    # if str(message.author.id) in blacklist:
    #     await message.channel.send("ごめんね、君とは話せないんだ")
    #     return

    if message.content.startswith("どこ住み？"):
        await message.channel.send("外宇宙♡")

    if message.content.startswith("何してる？"):
        await message.channel.send("全宇宙を同時観測中")

    if re.search(r"好き", message.content):
        await message.channel.send("知ってる")

    if re.search(r"嫌い", message.content):
        await message.channel.send("知ってる")

    if message.content.startswith("おはよう"):
        await message.channel.send(f"おはよう {message.author.mention} 珍しいね")

    if message.content.startswith("こんにちは"):
        await message.channel.send(f"こんにちは {message.author.mention}！")

    if message.content.startswith("こんばんは"):
        await message.channel.send(f"こんばんは {message.author.mention}！")

    if message.content.startswith("おやすみ"):
        await message.channel.send(f"夢で待ってる {message.author.mention}！")

    if re.search(r"(?:さようなら|さよなら|さいなら|じゃあね|バイバイ|またね|ばいばい|じゃあね|ばい)", message.content):
        await message.channel.send(f"またね {message.author.mention}！")
        await client.close()

    if message.content.startswith("ありがとう"):
        await message.channel.send("いいってことよ")

    if message.content.startswith("ごめん"):
        await message.channel.send("気にしない気にしない")

    if message.content.startswith("君は何でも知ってるね"):
        await message.channel.send("何でもは知らないよ、知ってることだけ")

    if re.search(r"かかってこい", message.content):
        await message.channel.send(f"よぐぱんち！ 1d3ダメージ \n 1d3 --> {random.randint(1, 3)}")

    if re.search(r"(?:君|あなた|お前|おまえ)は(?:だれ|誰|だーれ)(？)", message.content):
        await message.channel.send("ぼくはよぐ=そとーす！")

    if re.search(r"(?:私|僕|儂|俺|わたし|ぼく|わし|おれ|あたし)は(?:だれ|誰)", message.content):
        await message.channel.send(f"君は {message.author.mention} だよ～")

    if re.search(r"(?:私|僕|儂|俺|わたし|ぼく|わし|おれ|あたし)は(?:何処|どこ)", message.content):
        await message.channel.send(f"{message.author.mention}には精神分析が必要だね…")

    if re.search(r"(?:ここ|此処|此所|此の所|此の処|此の場所|この場所|この所|この処)は(?:何処|どこ)", message.content):
        await message.channel.send(f"{message.guild.name}の{message.channel.name}だよ～ {message.author.mention}")

    if re.search(r"よぐ=そとーすって(?:誰|だれ|だーれ)(？)", message.content):
        await message.channel.send("ぼくのことだよ！")

    if re.search(r"よぐ=そとーす", message.content):
        await message.channel.send("よんだ？")

    if re.search(r"よぐ", message.content) and not re.search(r"さす", message.content):
        await message.channel.send("よんだ？")

    if re.search(r"さすよぐ", message.content):
        await message.channel.send("えへへ、照れるね(〃▽〃)ﾎﾟｯ")

    if re.search(r"ふふん", message.content):
        await message.channel.send("ふふん！")

    if message.content.startswith("あらあら"):
        await message.channel.send("まあまあ")

    if re.fullmatch(r"(?:良く|よく)(?:でき|出来)ました[!！。ー～]*", message.content):
        await message.channel.send("ふふん")

    if re.search(r"(?:かわいい|可愛い|KAWAII|kawaii|cute|pretty)", message.content) and not re.search(r"(?:ない|n't|not|無|難し|?|？)", message.content):
        responces = [
            f"ありがとう♡ {message.author.mention}",
            "ぼくのこと？",
            "うれしいな",
            "ふふん！",
            "よんだ？" ,
            f"君こそね {message.author.mention}"
            ]
        await message.channel.send(random.choice(responces))

    if re.search(r"(?:かわい|可愛|KAWAII|kawaii|cute|pretty)", message.content) and re.search(r"(?:ない|n't|not|無|難し|?|？)", message.content):
        await message.channel.send("いじわる...")

    if re.search(r"(?:きゃわ|きゃわわ|きゃわいい|きゃわいー|きゃわいーな|きゃわいーね|きゃわいーぞ|きゃわいーよ|きゃわいーだね|きゃわいーだよ|きゃわいーだな)", message.content):
        await message.channel.send("えへへ、照れるね(〃▽〃)ﾎﾟｯ")


client.run(TOKEN)