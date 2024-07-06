import discord
from discord.ext import commands
import random
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(filename='gacha_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# 各ユーザーの使用回数を追跡する辞書
user_uses = {}
user_lowest_draws = {}
user_gacha_command_uses = {}

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Gacha!", style=discord.ButtonStyle.primary)
    async def gacha_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id not in user_uses:
            user_uses[user_id] = 0
            user_lowest_draws[user_id] = False
            user_gacha_command_uses[user_id] = 0

        # 確定排出までの残り回数
        remaining = 20 - user_uses[user_id]

        if user_gacha_command_uses[user_id] >= 10:
            if not interaction.response.is_done():
                await interaction.response.send_message("ガチャは10回までしか回せません。", ephemeral=True)
        elif user_uses[user_id] == 19 and not user_lowest_draws[user_id]:
            # 20回目に確定で一番排出率の低いURLを排出
            lowest_rate_url = get_lowest_rate_url()
            embed = discord.Embed(title="テストガチャ")
            embed.set_image(url=lowest_rate_url['url'])
            embed.add_field(name="Details", value=lowest_rate_url['details'], inline=False)
            embed.add_field(name="天井", value="天井です！", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # ログに保存
            user = interaction.user
            log_message = f"{user.name}#{user.discriminator} (ID: {user.id}) got (guaranteed) URL: {lowest_rate_url['url']} with details: {lowest_rate_url['details']}"
            logging.info(log_message)
            
            # 19回カウントをリセット（10回制限カウントはリセットしない）
            user_uses[user_id] = 0
            user_lowest_draws[user_id] = False
            
            # 10回制限カウントを増やす
            user_gacha_command_uses[user_id] += 1
        else:
            # ガチャの結果を送信する
            url_info = get_random_url()
            embed = discord.Embed(title="テストガチャ")
            embed.set_image(url=url_info['url'])
            embed.add_field(name="Details", value=url_info['details'], inline=False)
            embed.add_field(name="天井", value=f"天井まであと{remaining-1}回", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # ログに保存
            user = interaction.user
            log_message = f"{user.name}#{user.discriminator} (ID: {user.id}) got URL: {url_info['url']} with details: {url_info['details']}"
            logging.info(log_message)
            
            user_uses[user_id] += 1  # ユーザーごとのカウンターを更新
            user_gacha_command_uses[user_id] += 1  # 10回制限カウンターを更新

            # 最低排出率のURLを引いたかどうかを確認
            if url_info == get_lowest_rate_url():
                user_lowest_draws[user_id] = True
                user_uses[user_id] = 0  # カウントリセット

def get_random_url():
    # 仮のガチャデータ
    gacha_data = [
        {"url": "https://i.imgur.com/aXCB96U.png", "details": "Details 1", "rate": 0.01},  # 1%
        {"url": "https://i.imgur.com/KDq2CHJ.png", "details": "Details 2", "rate": 0.29},  # 29%
        {"url": "https://i.imgur.com/DehlAfs.png", "details": "Details 3", "rate": 0.70}   # 70%
    ]
    
    total_rate = sum(item["rate"] for item in gacha_data)
    random_value = random.uniform(0, total_rate)
    current_rate = 0
    
    for item in gacha_data:
        current_rate += item["rate"]
        if random_value <= current_rate:
            return item
    return gacha_data[-1]

def get_lowest_rate_url():
    # 仮のガチャデータ
    gacha_data = [
        {"url": "https://i.imgur.com/aXCB96U.png", "details": "Details 1", "rate": 0.01},  # 1%
        {"url": "https://i.imgur.com/KDq2CHJ.png", "details": "Details 2", "rate": 0.29},  # 29%
        {"url": "https://i.imgur.com/DehlAfs.png", "details": "Details 3", "rate": 0.70}   # 70%
    ]
    
    # 一番排出率の低いURLを取得
    return min(gacha_data, key=lambda x: x['rate'])

@bot.command()
async def gacha(ctx):
    view = GachaView()
    embed = discord.Embed(title="テストガチャ", description="ボタンを押してガチャを回してください。")
    await ctx.send(embed=embed, view=view)

    # 10回制限のカウントをリセット
    user_id = ctx.author.id
    if user_id in user_gacha_command_uses:
        user_gacha_command_uses[user_id] = 0
    else:
        user_gacha_command_uses[user_id] = 0

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# 環境変数からトークンを取得してボットを起動する
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)

