import discord
from discord.ext import commands
from discord import app_commands
from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree
from dotenv import load_dotenv
import asyncio
import os
import sys
import datetime
import requests
import json
import traceback

load_dotenv()

token = os.getenv("token")
version_hensuu = os.getenv("version_hensuu")

yuuyuu4621_ID = 892335593118392341

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

statuses = ["/help | タムタムん家 管理bot", "/help | Version 0.01"]

async def change_status():
    while True:
        for status in statuses:
            await bot.change_presence(activity=discord.Game(name=status))
            await asyncio.sleep(60)

@bot.event
async def on_ready():
    print (f'Logged in as {bot.user}')
    bot.loop.create_task(change_status())

    login_channel = bot.get_channel(1242327958195011624)
    login_time = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    login_embed = discord.Embed(
        title="**起動しました**",
        description=f"{login_time} {bot.user} **起動**しました",
        color=discord.Color.blue()
    )
    if login_channel:
        await login_channel.send (embed=login_embed)
    else:
        print ("チャンネルが見つかりません")

@bot.tree.command(name="version", description="現在のバージョンを表示します")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(f"現在のバージョンは {version_hensuu} です")

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
    current_time = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    await interaction.response.send_message(f"現在の時刻は {current_time} (日本標準時(GMT+9)) です")
    print (f"現在の時刻は {current_time} (日本標準時(GMT+9)) です")

@bot.tree.command(name="ping", description="pingを送信します")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    print ("Pong!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("指定されたチャンネルが見つかりません。")

@bot.tree.command(name="message", description="指定されたチャンネルにメッセージを送信します")
async def send_message(interaction: discord.Interaction, channel_id: str, *, message: str):
    try:
        channel_id = int(channel_id)
        channel = bot.get_channel(channel_id)
        if channel:
            formatted_message = message.replace("\\n", "\n")
            await channel.send(formatted_message)
            await interaction.response.send_message(f"メッセージを {channel.mention} に送信しました。")
        else:
            await interaction.response.send_message("指定されたチャンネルが見つかりません。")
    except discord.Forbidden:
        await interaction.response.send_message("指定されたチャンネルにメッセージを送信する権限がありません。")
    except ValueError:
        await interaction.response.send_message("有効な整数を入力してください。")
    except Exception as e:
        await interaction.response.send_message(f"エラーが発生しました: {e}")

@bot.tree.command(name="kick", description="指定されたプレイヤーをキックします")
@app_commands.describe(user="キックするユーザーの名前", reason="キックする理由")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("あなたにはこのコマンドを実行する権限がありません。")
        return

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
        logout_channel = bot.get_channel(1242327958195011624)
        logout_time = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        logout_embed = discord.Embed(
        title="**停止しました**",
        description=f"{logout_time} {bot.user} **停止**しました",
        color=discord.Color.red()
    )
        if user_id == yuuyuu4621_ID:
            if logout_channel:
                await interaction.response.send_message("停止します")
                await logout_channel.send(embed=logout_embed)
                await bot.close()
            else:
                print ("チャンネルが見つかりません")
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
        restart_channel = bot.get_channel(1242327958195011624)
        restart_time = datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
        restart_embed = discord.Embed(
        title="**停止しました**",
        description=f"{restart_time} {bot.user} **停止**しました",
        color=discord.Color.red()
    )
        if user_id == yuuyuu4621_ID:
            if restart_channel:
                await interaction.response.send_message("再起動します")
                await restart_channel.send(embed=restart_embed)
                await restart_bot()
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

    @discord.app_commands.command(name="logclear", description="コンソールのログをクリアします")
    async def logclear(self, interaction: discord.Interaction):
        if interaction.user.id == yuuyuu4621_ID:
            await interaction.response.send_message("コンソールのログをクリアしました")
            clear_console()
        else:
            await interaction.response.send_message("あなたには実行権限がありません")

def clear_console():
    if os.name == 'nt':
        os.system('cls')

async def restart_bot():
    python = sys.executable
    os.execl(python, python, *sys.argv)

admin_group = AdminCommands()
bot.tree.add_command(admin_group)

bot.run(token)