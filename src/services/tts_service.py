from gtts import gTTS
import os
import discord
import asyncio
import logging

logger = logging.getLogger('discord_bot')

class TTSService:
    def __init__(self):
        self.temp_file = "message.mp3"
        logger.info("TTS service initialized")

    async def text_to_speech(self, text: str, voice_client: discord.VoiceClient):
        try:
            # 最大20文字に制限
            text = text[:20]
            
            # 音声ファイルを生成
            tts = gTTS(text=text, lang='ja')
            tts.save(self.temp_file)
            
            # ボイスチャンネルでメッセージを再生
            voice_client.play(
                discord.FFmpegPCMAudio(
                    self.temp_file,
                    options="-filter:a atempo=2.0"
                ),
                after=lambda e: logger.error(f"TTS playback error: {e}") if e else None
            )
            
            # 再生終了を待機
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # 一時ファイルを削除
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
                
        except Exception as e:
            logger.error(f"Error in TTS processing: {e}")
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
            raise
