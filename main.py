import os
import sys
import logging
from datetime import time, timezone, timedelta

# Windows環境でのUnicodeEncodeError (絵文字など) 対策
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from config_manager import get_weather_channel_id, set_weather_channel_id
from weather import fetch_tokyo_weather, create_weather_embed, JST

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("discord_bot")

# .env ファイルから環境変数を読み込む
load_dotenv()

# Discord Botトークンの取得
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN or TOKEN == "your_bot_token_here":
    logger.error("DISCORD_TOKEN が設定されていません。")
    logger.error(".env ファイルを作成し、Discord Developer Portalから取得したBotトークンを設定してください。")
    sys.exit(1)

# インテントの設定 (メッセージ内容取得を含む)
intents = discord.Intents.default()
intents.message_content = True

# Botインスタンスの生成 (コマンドプレフィックスは '!')
bot = commands.Bot(command_prefix="!", intents=intents)

# 毎日朝7:00 (JST) の実行時刻を設定
NOTIFY_TIME = time(hour=7, minute=0, second=0, tzinfo=JST)


@tasks.loop(time=NOTIFY_TIME)
async def daily_weather_task():
    """毎日朝7時(JST)に東京の天気を指定チャンネルへ通知するタスク"""
    logger.info("朝7時の天気通知タスクを実行します。")
    channel_id = get_weather_channel_id()
    if not channel_id:
        logger.warning("天気通知先のチャンネルIDが設定されていません。/set_weather_channel で設定してください。")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            logger.error(f"通知先チャンネル (ID: {channel_id}) の取得に失敗しました: {e}")
            return

    # 天気情報を取得
    weather_data = await fetch_tokyo_weather()
    if not weather_data:
        logger.error("天気情報の取得に失敗しました。")
        await channel.send("⚠️ 今日の天気情報の取得に失敗しました。")
        return

    # Embed を作成して送信
    embed = create_weather_embed(weather_data, title_prefix="東京の朝7時 天気予報")
    try:
        await channel.send(embed=embed)
        logger.info(f"チャンネル (ID: {channel_id}) に天気予報を通知しました。")
    except Exception as e:
        logger.error(f"天気予報のメッセージ送信に失敗しました: {e}")


@daily_weather_task.before_loop
async def before_daily_weather_task():
    """Botの起動・ログインが完了するまでタスクの開始を待機"""
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    """Bot起動時に呼び出されるイベント"""
    logger.info(f"ログイン完了: {bot.user} (ID: {bot.user.id})")

    # スラッシュコマンドの同期
    try:
        synced = await bot.tree.sync()
        logger.info(f"スラッシュコマンド同期完了: {len(synced)} 件のコマンドを同期しました。")
    except Exception as e:
        logger.error(f"コマンド同期エラー: {e}")

    # 朝7時定期通知ループの開始 (多重起動を防止)
    if not daily_weather_task.is_running():
        daily_weather_task.start()
        logger.info(f"朝7時定期通知タスクを開始しました (設定時刻: {NOTIFY_TIME.strftime('%H:%M')} JST)。")

    # 現在の通知先チャンネルの確認ログ
    current_channel_id = get_weather_channel_id()
    if current_channel_id:
        logger.info(f"現在の天気通知先チャンネルID: {current_channel_id}")
    else:
        logger.info("天気通知先チャンネルは未設定です。/set_weather_channel で設定できます。")

    logger.info("Botは現在待機中です。メッセージまたはコマンドを受信できます。")


@bot.tree.command(name="hello", description="Hello Worldと返答します。")
async def slash_hello(interaction: discord.Interaction):
    """スラッシュコマンド /hello のハンドラ"""
    logger.info(f"/hello コマンド実行: ユーザー={interaction.user}")
    await interaction.response.send_message("Hello World!")


@bot.command(name="hello")
async def cmd_hello(ctx: commands.Context):
    """プレフィックスコマンド !hello のハンドラ"""
    logger.info(f"!hello コマンド実行: ユーザー={ctx.author}")
    await ctx.send("Hello World!")


@bot.tree.command(name="weather", description="東京の今日の天気をすぐに確認します。")
async def slash_weather(interaction: discord.Interaction):
    """スラッシュコマンド /weather のハンドラ"""
    logger.info(f"/weather コマンド実行: ユーザー={interaction.user}")
    # API呼び出しの待機中にDiscord側がタイムアウト(3秒)しないよう待機状態にする
    await interaction.response.defer()

    weather_data = await fetch_tokyo_weather()
    if not weather_data:
        await interaction.followup.send("⚠️ 天気情報の取得に失敗しました。時間をおいて再試行してください。")
        return

    embed = create_weather_embed(weather_data)
    await interaction.followup.send(embed=embed)


@bot.command(name="weather")
async def cmd_weather(ctx: commands.Context):
    """プレフィックスコマンド !weather のハンドラ"""
    logger.info(f"!weather コマンド実行: ユーザー={ctx.author}")
    async with ctx.typing():
        weather_data = await fetch_tokyo_weather()
        if not weather_data:
            await ctx.send("⚠️ 天気情報の取得に失敗しました。時間をおいて再試行してください。")
            return
        embed = create_weather_embed(weather_data)
        await ctx.send(embed=embed)


@bot.tree.command(name="set_weather_channel", description="このチャンネルを毎朝7時の天気通知先に設定します。")
async def slash_set_weather_channel(interaction: discord.Interaction):
    """スラッシュコマンド /set_weather_channel のハンドラ"""
    channel = interaction.channel
    success = set_weather_channel_id(channel.id)
    if success:
        logger.info(f"天気通知先チャンネルを設定しました: {channel.name} (ID: {channel.id})")
        await interaction.response.send_message(
            f"✅ 毎朝7時の東京天気通知先を **#{channel.name}** に設定しました！"
        )
    else:
        await interaction.response.send_message(
            "❌ 設定の保存に失敗しました。ボットの権限またはファイルパーミッションを確認してください。",
            ephemeral=True
        )


@bot.command(name="set_weather_channel")
@commands.has_permissions(manage_channels=True)
async def cmd_set_weather_channel(ctx: commands.Context):
    """プレフィックスコマンド !set_weather_channel のハンドラ"""
    channel = ctx.channel
    success = set_weather_channel_id(channel.id)
    if success:
        logger.info(f"天気通知先チャンネルを設定しました: {channel.name} (ID: {channel.id})")
        await ctx.send(f"✅ 毎朝7時の東京天気通知先を **#{channel.name}** に設定しました！")
    else:
        await ctx.send("❌ 設定の保存に失敗しました。")


@bot.event
async def on_message(message: discord.Message):
    """メッセージ受信時のイベント"""
    # Bot自身のメッセージは無視する
    if message.author.bot:
        return

    # コマンドの処理を実行
    await bot.process_commands(message)


def main():
    """エントリーポイント"""
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
