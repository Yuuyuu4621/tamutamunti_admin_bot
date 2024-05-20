import discord
from discord.ext import commands
from discord import app_commands
from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree
from dotenv import load_dotenv
import os
import sys
import datetime
import requests
import json
import traceback

# token
load_dotenv()

token = os.getenv("token")
version = os.getenv("version")
webhook = os.getenv("webhook")

# WEBHOOKURL
WEBHOOK_URL = webhook

# エラーメッセージをWebhookに送信する関数
def send_error_message(error_message):
    embed = {
        "title": "エラーが発生しました",
        "description": error_message,
        "color": 0xFF0000  # 赤色
    }
    
    payload = {
        "content": "エラーが発生しました。",
        "embeds": [embed]
    }

    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        if response.status_code in (200, 204):
            print("エラーメッセージを送信しました。")
        else:
            print(f"エラーメッセージの送信に失敗しました。ステータスコード: {response.status_code}")
    except Exception as e:
        print(f"エラーメッセージの送信中にエラーが発生しました: {e}")

# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True

# Botの初期化
bot = commands.Bot(command_prefix="/", intents=intents)
CHANNEL_ID = 1217753256076378152
ALLOWED_SERVER_ID = 1197911092861612073

# コマンドの設定

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="テスト"))

@bot.event
async def on_command_error(ctx, error):
    # エラーメッセージをWebhookに送信
    error_message = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    send_error_message(error_message)
    # エラーをコンソールに出力
    print(f"エラー: {error_message}")

@bot.tree.command(name="version", description="現在のバージョンを表示します")
async def version(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_SERVER_ID:
            await interaction.response.send_message("このサーバーではこのコマンドを使用できません。")
    await interaction.response.send_message(f"現在のバージョンは {version} です")

@bot.tree.command(name="join", description="ボイスチャンネルに参加します")
async def join(interaction: discord.Interaction):
    # メンバー情報を取得
    member = interaction.guild.get_member(interaction.user.id)
    # メンバーがボイスチャンネルに接続しているかどうかを確認
    if member.voice:
        # メンバーがいるボイスチャンネルを取得
        channel = member.voice.channel
        # ボイスクライアントがすでに接続していない場合に接続
        if interaction.guild.voice_client is None:
            await channel.connect()
            await interaction.response.send_message("ボイスチャンネルに参加しました。")
        else:
            await interaction.response.send_message("既にボイスチャンネルに接続しています。")
    else:
        await interaction.response.send_message("ボイスチャンネルに接続していません。")


@bot.tree.command(name="leave", description="ボイスチャンネルから退出します")
async def leave(interaction: discord.Interaction):
    # メンバー情報を取得
    member = interaction.guild.get_member(interaction.user.id)
    # メンバーがボイスチャンネルに接続しているかどうかを確認
    if member.voice:
        # ボイスチャンネルから接続しているボイスクライアントを取得
        vc = member.voice.channel.guild.voice_client
        # ボイスクライアントが接続しているかどうかを確認
        if vc:
            # ボイスチャンネルから退出
            await vc.disconnect()
            await interaction.response.send_message("ボイスチャンネルから退出しました。")
        else:
            await interaction.response.send_message("ボイスチャンネルに接続していません。")
    else:
        await interaction.response.send_message("ボイスチャンネルに接続していません。")


@bot.tree.command(name="time", description="現在の時刻を表示します")
async def time(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_SERVER_ID:
            await interaction.response.send_message("このサーバーではこのコマンドを使用できません。")
    current_time = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    await interaction.response.send_message(f"現在の時刻は {current_time} (日本標準時(GMT+9)) です")
    print (f"現在の時刻は {current_time} (日本標準時(GMT+9)) です")

@bot.tree.command(name="ping", description="pingを送信します")
async def ping(interaction: discord.Interaction):
    if interaction.guild.id != ALLOWED_SERVER_ID:
            await interaction.response.send_message("このサーバーではこのコマンドを使用できません。")
    await interaction.response.send_message("Pong!")
    print ("Pong!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("指定されたチャンネルが見つかりません。")

@bot.tree.command(name="message", description="指定されたチャンネルにメッセージを送信します")
async def send_message(ctx, channel_id: str, *, message: str):
    try:
        channel_id = int(channel_id)
        channel = bot.get_channel(channel_id)
        if channel:
            Interaction.response.send_message(message)
            await Interaction.response.send_message(f"メッセージを {channel.mention} に送信しました。")
        else:
            Interaction.response.send_message("指定されたチャンネルが見つかりません。")
    except discord.Forbidden:
        Interaction.response.send_message("指定されたチャンネルにメッセージを送信する権限がありません。")
    except ValueError:
        Interaction.response.send_message("有効な整数を入力してください。")
    except Exception as e:
        Interaction.response.send_message(f"エラーが発生しました: {e}")


@bot.tree.command(name="kick", description="指定されたプレイヤーをキックします")
@app_commands.describe(user="キックするユーザーの名前", reason="キックする理由")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    # キックするユーザーの名前を取得
    try:
        await user.kick(reason=f"{reason} (Kicked by {interaction.user.name})")
        await interaction.response.send_message(f"{user.name} はキックされました。 理由: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("キック権限がありません。")
    except discord.HTTPException:
        await interaction.response.send_message("キックに失敗しました。")

@bot.tree.command(name="ban", description="指定されたプレイヤーをBANします")
@app_commands.describe(user="ユーザーの名 / ID", reason="理由")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    # キックするユーザーの名前を取得
    try:
        await user.ban(reason=f"{reason} (Banned by {interaction.user.name})")
        await interaction.response.send_message(f"{user.name} はBANされました。 理由: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("BAN権限がありません。")
    except discord.HTTPException:
        await interaction.response.send_message("BANに失敗しました。")

from discord.ext import commands

# 例としてのユーザーID
yuuyuu4621_ID = 892335593118392341

@bot.tree.command(name="clear", description="指定した数のメッセージを削除します")
@app_commands.describe(count="数")
async def clear(interaction: discord.Interaction, count: int):
    try:
        # コマンドを実行したユーザーのIDを取得
        user_id = interaction.user.id
        
        # IDが許可されたものであるかを確認
        if user_id == yuuyuu4621_ID:
            await interaction.channel.purge(limit=count)
            # interactionが有効な場合にのみメッセージを送信
            if interaction.response:
                await interaction.response.send_message(f"{count}個のメッセージを削除しました。")
        else:
            # IDが許可されていない場合
            await interaction.response.send_message("権限がありません。")
    except discord.Forbidden:
        await interaction.response.send_message("メッセージ管理権限がありません。")
    except discord.NotFound:
        # インタラクションが見つからない場合の処理
        pass

# /embed コマンドの定義
@bot.tree.command(name="embed", description="Embedを作成して送信します")
async def embed(interaction: discord.Interaction):
    # ユーザーを取得
    user = await bot.fetch_user(interaction.user.id)
    if user is None:  # ユーザーが見つからない場合
        await interaction.response.send_message("ユーザーが見つかりませんでした。")
        return

    # 埋め込みメッセージを作成
    embed = discord.Embed(
        title="Embedメッセージのタイトル",
        description="Embedメッセージの説明",
        color=discord.Color.red()  # 埋め込みメッセージの色
    )
    # フィールドを追加
    embed.add_field(name="フィールド名1", value="フィールド値1", inline=False)
    embed.add_field(name="フィールド名2", value="フィールド値2", inline=True)
    # 画像を追加
    embed.set_image(url="https://example.com/image.jpg")
    
    # ユーザーの名前とアバターを表示
    if user.avatar:
        avatar_url = user.avatar.url
    else:
        avatar_url = user.default_avatar.url
    embed.set_footer(text=f"{user.name}#{user.discriminator} が送信", icon_url=avatar_url)
    
    # メッセージを送信
    await interaction.response.send_message(embed=embed)

class AdminCommands(discord.app_commands.Group):
    def __init__(self):
        super().__init__(name="admin", description="管理コマンド")

    @discord.app_commands.command(name="stop", description="ボットを停止します")
    async def stop(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id == yuuyuu4621_ID:
            await interaction.response.send_message("停止します")
            await bot.close()
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

    @discord.app_commands.command(name="dm", description="指定したユーザーにDMを送ります")
    async def dm(self, interaction: discord.Interaction, user_id: str, message: str):  # ユーザーIDを文字列として受け取る
        if interaction.user.id == yuuyuu4621_ID:
            try:
                user = await bot.fetch_user(int(user_id))  # ユーザーIDを整数に変換
                await user.send(message)
                await interaction.response.send_message(f"ユーザー {user_id} にメッセージを送りました。")
            except discord.NotFound:
                await interaction.response.send_message(f"ユーザー {user_id} が見つかりません。")
            except discord.Forbidden:
                await interaction.response.send_message(f"ユーザー {user_id} にDMを送る権限がありません。")
            except discord.HTTPException as e:
                await interaction.response.send_message(f"メッセージの送信中にエラーが発生しました: {e}")
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

    @discord.app_commands.command(name="leave", description="指定したサーバーからボットを退出させます")
    async def leave(self, interaction: discord.Interaction, server_id: str):
        if interaction.user.id == yuuyuu4621_ID:
            guild = bot.get_guild(int(server_id))
            if guild:
                try:
                    await guild.leave()
                    await interaction.response.send_message(f"サーバー {server_id} からボットを退出させました。")
                except discord.Forbidden:
                    await interaction.response.send_message(f"ボットにサーバー {server_id} から退出する権限がありません。")
            else:
                await interaction.response.send_message(f"サーバー {server_id} が見つかりません。")
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

    @discord.app_commands.command(name="restart", description="ボットを再起動します")
    async def restart(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id == yuuyuu4621_ID:
            await interaction.response.send_message("再起動します...")
            await restart_bot()
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

    @discord.app_commands.command(name="logclear", description="コンソールのログをクリアします")
    async def logclear(self, interaction: discord.Interaction):
        if interaction.guild.id != ALLOWED_SERVER_ID:
            await interaction.response.send_message("このサーバーではこのコマンドを使用できません。")
        if interaction.user.id == yuuyuu4621_ID:
            await interaction.response.send_message("ログをクリアしています...")
            clear_console()
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

def clear_console():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix系
        os.system('clear')

async def restart_bot():
    python = sys.executable
    os.execl(python, python, *sys.argv)

admin_group = AdminCommands()
bot.tree.add_command(admin_group)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="テスト"))

# すべてのコマンドを許可されたサーバーでのみ実行可能にするミドルウェア
@bot.check
async def globally_block_dms(ctx):
    if ctx.guild and ctx.guild.id == ALLOWED_SERVER_ID:
        return True
    await ctx.send("このサーバーではこのボットを使用できません。")
    return False

# ボットを実行
bot.run(token)