import discord
from discord import app_commands
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('discord_bot')

class CommandHandler:
    def __init__(self, gemini_service, tts_service):
        self.gemini_service = gemini_service
        self.tts_service = tts_service
        self.selected_text_channel = {}
        self.selected_voice_channel = {}

    async def fetch_messages(self, channel, num=0):
        try:
            messages = []
            if num == 0:
                one_day_ago = datetime.utcnow() - timedelta(days=1)
                async for message in channel.history(after=one_day_ago):
                    if not message.author.bot:
                        messages.append(message)
            else:
                async for message in channel.history(limit=num):
                    if not message.author.bot:
                        messages.append(message)

            return "\n".join([f"{message.author}: {message.content}" for message in messages])
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise

    async def fetch_user_messages(self, user_id, guild):
        try:
            messages = []
            for channel in guild.channels:
                try:
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
                    logger.error(f"Error fetching from channel {channel.name}: {e}")
                    continue

            return "\n".join([f"{message.author}: {message.content}" for message in messages])
        except Exception as e:
            logger.error(f"Error in fetch_user_messages: {e}")
            raise

    # コマンドハンドラーメソッド
    async def handle_summary(self, interaction: discord.Interaction, silent: bool = False):
        try:
            await interaction.response.defer(ephemeral=silent)
            messages = await self.fetch_messages(interaction.channel, 0)
            embed = await self.gemini_service.summarize(messages, "要約結果")
            await interaction.followup.send(embed=embed)
            if not silent:
                await interaction.followup.send("処理が終了しました")
        except Exception as e:
            logger.error(f"Error in summary command: {e}")
            await interaction.followup.send("エラーが発生しました", ephemeral=True)

    async def handle_mvp(self, interaction: discord.Interaction, silent: bool = False):
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
