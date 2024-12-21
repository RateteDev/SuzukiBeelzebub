import discord
from discord import app_commands
import logging
from datetime import datetime, timedelta

# ロガーの設定
logger = logging.getLogger('discord_bot')

class CommandHandler:
    def __init__(self, gemini_service, tts_service):
        # GeminiサービスとTTSサービスのインスタンスを保持
        self.gemini_service = gemini_service
        self.tts_service = tts_service
        # 選択中のテキストチャンネルとボイスチャンネルを保持する辞書
        self.selected_text_channel = {}
        self.selected_voice_channel = {}

    async def fetch_messages(self, channel, num=0):
        # 指定されたチャンネルからメッセージを取得する関数
        try:
            messages = []
            # numが0の場合は過去1日分のメッセージを取得、それ以外の場合はnum件のメッセージを取得
            if num == 0:
                one_day_ago = datetime.utcnow() - timedelta(days=1)
                async for message in channel.history(after=one_day_ago):
                    if not message.author.bot:
                        messages.append(message)
            else:
                async for message in channel.history(limit=num):
                    if not message.author.bot:
                        messages.append(message)

            # メッセージリストを整形して返す
            return "\n".join([f"{message.author}: {message.content}" for message in messages])
        except Exception as e:
            # エラー発生時はログを出力して例外を再送出
            logger.error(f"Error fetching messages: {e}")
            raise

    async def fetch_user_messages(self, user_id, guild):
        # 指定されたユーザーIDとGuildからメッセージを取得する関数
        try:
            messages = []
            # Guild内の全チャンネルをループ
            for channel in guild.channels:
                try:
                    # テキストチャンネルとフォーラムチャンネルからメッセージを取得
                    if isinstance(channel, discord.TextChannel):
                        logger.info(f"Fetching from text channel: {channel.name}")
                        async for message in channel.history(limit=100):
                            if message.author.id == user_id:
                                messages.append(message)
                    elif isinstance(channel, discord.ForumChannel):
                        logger.info(f"Fetching from forum channel: {channel.name}")
                        for thread in channel.threads:
                            async for message in thread.history(limit=100):
                                if message.author.id == user_id:
                                    messages.append(message)
                except Exception as e:
                    # エラー発生時はログを出力して次のチャンネルへ
                    logger.error(f"Error fetching from channel {channel.name}: {e}")
                    continue

            # メッセージリストを整形して返す
            return "\n".join([f"{message.author}: {message.content}" for message in messages])
        except Exception as e:
            # エラー発生時はログを出力して例外を再送出
            logger.error(f"Error in fetch_user_messages: {e}")
            raise

    # コマンドハンドラーメソッド群

    async def handle_summary(self, interaction: discord.Interaction, silent: bool = False):
        # メッセージを要約するコマンドハンドラー
        try:
            await interaction.response.defer(ephemeral=silent) #応答を遅延させる
            messages = await self.fetch_messages(interaction.channel, 0) #過去1日分のメッセージを取得
            embed = await self.gemini_service.summarize(messages, "要約結果") #Geminiで要約
            await interaction.followup.send(embed=embed) #結果を送信
            if not silent:
                await interaction.followup.send("処理が終了しました") #処理完了メッセージ
        except Exception as e:
            logger.error(f"Error in summary command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)

    async def handle_mvp(self, interaction: discord.Interaction, silent: bool = False):
        # MVP(最も印象的な発言)を選出するコマンドハンドラー
        try:
            await interaction.response.defer(ephemeral=silent)
            messages = await self.fetch_messages(interaction.channel, 0)
            embed = await self.gemini_service.summarize(messages, "MVP", "次の文章からMVP(最も格好良い発言)を選んでください：\n")
            await interaction.followup.send(embed=embed)
            if not silent:
                await interaction.followup.send("処理が終了しました")
        except Exception as e:
            logger.error(f"Error in MVP command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)

    async def handle_personality_analysis(self, interaction: discord.Interaction, analysis_type: str, silent: bool = False):
        # ユーザーの性格を分析するコマンドハンドラー
        try:
            await interaction.response.defer(ephemeral=silent)
            messages = await self.fetch_user_messages(interaction.user.id, interaction.guild)
            embed = await self.gemini_service.analyze_personality(messages, interaction.user.name, analysis_type)
            await interaction.followup.send(embed=embed)
            if not silent:
                await interaction.followup.send("処理が終了しました")
        except Exception as e:
            logger.error(f"Error in personality analysis command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)

    async def handle_voice_join(self, interaction: discord.Interaction):
        # ボットをボイスチャンネルに参加させるコマンドハンドラー
        try:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
                self.selected_text_channel[interaction.guild.id] = interaction.channel.id
                self.selected_voice_channel[interaction.guild.id] = channel.id
                await interaction.response.send_message(f"{channel}に参加しました", ephemeral=True)
            else:
                await interaction.response.send_message("まずVCに参加してください", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in voice join command: {e}")
            await interaction.response.send_message("エラーが発生しました", ephemeral=True)

    async def handle_voice_leave(self, interaction: discord.Interaction):
        # ボットをボイスチャンネルから退出させるコマンドハンドラー
        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                self.selected_text_channel.pop(interaction.guild.id, None)
                self.selected_voice_channel.pop(interaction.guild.id, None)
                await interaction.response.send_message("VCから退出しました", ephemeral=True)
            else:
                await interaction.response.send_message("VCに接続していません", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in voice leave command: {e}")
            await interaction.response.send_message("エラーが発生しました", ephemeral=True)

    async def handle_imakita(self, interaction: discord.Interaction, silent: bool = False):
        # 過去のメッセージを3行に要約するコマンドハンドラー
        try:
            await interaction.response.defer(ephemeral=silent)
            messages = await self.fetch_messages(interaction.channel, 100)
            embed = await self.gemini_service.summarize(messages, "今北産業", "次の文章を3行で要約してください：\n")
            await interaction.followup.send(embed=embed)
            if not silent:
                await interaction.followup.send("処理が終了しました")
        except Exception as e:
            logger.error(f"Error in imakita command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)

    async def handle_age_estimation(self, interaction: discord.Interaction, silent: bool = False):
        # ユーザーの年齢を推定するコマンドハンドラー
        try:
            await interaction.response.defer(ephemeral=silent)
            messages = await self.fetch_user_messages(interaction.user.id, interaction.guild)
            embed = await self.gemini_service.analyze_age(messages, interaction.user.name)
            await interaction.followup.send(embed=embed)
            if not silent:
                await interaction.followup.send("処理が終了しました")
        except Exception as e:
            logger.error(f"Error in age estimation command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)
