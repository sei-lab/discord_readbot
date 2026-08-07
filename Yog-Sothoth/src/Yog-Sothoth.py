import discord
import os
from dotenv import load_dotenv
import re
import random
import datetime
import zoneinfo

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

talk_list = []

# @client.event
# async def on_ready():
#     channel = client.get_channel(1532005786883063858)  # Replace with your channel ID
#     await channel.send("よぐ=そとーす参上！")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    blacklist = ["",""] 
    if str(message.author.id) in blacklist:
        return

    if re.search(r"よぐ", message.content) and not re.search(r"さす", message.content) and not re.search(r"よぐぱんち", message.content) and not message.author.id in talk_list:
        await message.channel.send("よんだ？")
        talk_list.append(message.author.id)
        return

    if not message.author.id in talk_list:
        return

    if re.search(r"(?:さようなら|さよなら|さいなら|じゃあね|バイバイ|またね|ばいばい)", message.content):
        await message.channel.send(f"またね {message.author.mention}！")
        talk_list.remove(message.author.id)
        return

    if message.content.startswith("どこ住み？"):
        await message.channel.send("外宇宙♡")
        return

    if re.search(r"(?:何|なに)して", message.content) and re.search(r"(?:？|\?)"):
        await message.channel.send("いまね、全宇宙を同時観測中！")
        return

    if re.search(r"(?:好き|すき♡)", message.content):
        await message.channel.send("知ってる")
        return

    if re.search(r"嫌い", message.content):
        await message.channel.send("知ってる")
        return

    if message.content.startswith("おはよう"):
        await message.channel.send(f"おはよう {message.author.mention}！")
        return

    if message.content.startswith("こんにちは"):
        await message.channel.send(f"こんにちは {message.author.mention}！")
        return

    if message.content.startswith("こんばんは"):
        await message.channel.send(f"こんばんは {message.author.mention}！")
        return

    if message.content.startswith("おやすみ"):
        await message.channel.send(f"夢で待ってる {message.author.mention}！")
        return

    if message.content.startswith("ありがとう"):
        await message.channel.send("いいってことよ")
        return

    if message.content.startswith("ごめん"):
        await message.channel.send("気にしない気にしない")
        return

    if message.content.startswith("君は何でも知ってるね"):
        await message.channel.send("何でもは知らないよ、知ってることだけ")
        return

    if re.search(r"かかってこい", message.content):
        await message.channel.send(f"よぐぱんち！ 1d3ダメージ")
        return

    if re.search(r"(?:君|あなた|お前|おまえ)は(?:だれ|誰|だーれ)(？)", message.content):
        await message.channel.send("ぼくはよぐ=そとーす！")
        return

    if re.search(r"(?:私|僕|儂|俺|我|わたし|ぼく|わし|おれ|あたし|われ)は(?:だれ|誰)", message.content):
        await message.channel.send(f"君は {message.author.mention} だよ～")
        return

    if re.search(r"(?:私|僕|儂|俺|我|わたし|ぼく|わし|おれ|あたし|われ)は(?:何処|どこ)", message.content):
        await message.channel.send(f"{message.author.mention}には精神分析が必要だね…")
        return

    if re.search(r"(?:ここ|此処|此所|此の所|此の処|此の場所|この場所|この所|この処)は(?:何処|どこ)", message.content):
        await message.channel.send(f"{message.guild.name}の{message.channel.name}だよ～ {message.author.mention}")
        return

    if re.search(r"よぐ=そとーすって(?:誰|だれ|だーれ)(？)", message.content):
        await message.channel.send("ぼくのことだよ！")
        return

    if re.search(r"さすよぐ", message.content):
        await message.channel.send("えへへ、照れるね(〃▽〃)ﾎﾟｯ")
        return

    if re.search(r"ふふん", message.content):
        await message.channel.send("ふふん！")
        return

    if message.content.startswith("あらあら"):
        await message.channel.send("まあまあ")
        return

    if re.fullmatch(r"(?:良く|よく)(?:でき|出来)ました[!！。ー～]*", message.content):
        await message.channel.send("ふふん")
        return
    
    if re.search(r"(?:かわいい|可愛い|KAWAII|kawaii|cute|pretty)", message.content) and not re.search(r"(?:ない|n't|no|無|難|非|No|難い|ず|\?|？)", message.content):
        responces = [
            f"ありがとう♡ {message.author.mention}",
            "ぼくのこと？",
            "うれしいな",
            "ふふん！",
            "よんだ？" ,
            f"君こそね {message.author.mention}"
            ]
        await message.channel.send(random.choice(responces))
        return

    if re.search(r"(?:かわい|可愛|KAWAII|kawaii|cute|pretty)", message.content) and re.search(r"(?:ない|n't|no|無|難|非|No|がたい|ず|\?|？)", message.content):
        await message.channel.send("いじわる...")
        return

    if re.search(r"(?:きゃわ|きゃわわ|きゃわいい|きゃわいー|きゃわいーな|きゃわいーね|きゃわいーぞ|きゃわいーよ|きゃわいーだね|きゃわいーだよ|きゃわいーだな)", message.content):
        await message.channel.send("えへへ、照れるね(〃▽〃)ﾎﾟｯ")
        return

    if re.search(r"よぐ", message.content) and not re.search(r"さす", message.content) and not re.search(r"よぐぱんち", message.content):
        responces = [
            "聞いてるよ～",
            "なになに？",
            "どうしたの？",
            "はいは～い",
            "！！"
        ]
        await message.channel.send(random.choice(responces))
        return


client.run(TOKEN)