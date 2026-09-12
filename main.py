import os
import sys
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

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


@bot.event
async def on_message(message: discord.Message):
    """メッセージ受信時のイベント"""
    # Bot自身のメッセージは無視する
    if message.author.bot:
        return

    # コマンドの処理を実行 (プレフィックスコマンドを処理するため必須)
    await bot.process_commands(message)


def main():
    """エントリーポイント"""
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
