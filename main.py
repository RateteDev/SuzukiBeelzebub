import os
from dotenv import load_dotenv
import discord
from src.discord_bot.bot import DiscordBot
from src.services.gemini_service import GeminiService
from src.services.tts_service import TTSService
from src.utils.logger import setup_logger

def main():
    # ロガーのセットアップ
    logger = setup_logger()
    logger.info("Starting bot initialization")

    # 環境変数の読み込み
    load_dotenv()
    api_token = os.getenv('MY_API_TOKEN')
    api_key = os.getenv('MY_API_KEY')

    if api_token is None or api_key is None:
        raise ValueError("Required environment variables are not set")

    # Intentの設定
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.voice_states = True
    intents.message_content = True

    # サービスの初期化
    gemini_service = GeminiService(api_key)
    tts_service = TTSService()

    # Botの初期化と実行
    bot = DiscordBot(
        gemini_service=gemini_service,
        tts_service=tts_service,
        intents=intents
    )

    logger.info("Bot initialization completed, starting client")
    bot.run(api_token)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Critical error: {e}", flush=True)
