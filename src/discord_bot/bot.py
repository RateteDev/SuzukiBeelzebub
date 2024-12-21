import discord
from discord import app_commands
import logging
from .commands import CommandHandler
from ..utils.message_cleaner import MessageCleaner

logger = logging.getLogger('discord_bot')

class DiscordBot(discord.Client):
    def __init__(self, gemini_service, tts_service, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.command_handler = CommandHandler(gemini_service, tts_service)
        self.message_cleaner = MessageCleaner()
        self.setup_commands()

    def setup_commands(self):
        @self.tree.command(name="要約", description="過去一日分のメッセージを要約します")
        async def summarize(interaction: discord.Interaction):
            await self.command_handler.handle_summary(interaction)

        @self.tree.command(name="mvp", description="24時間のMVP")
        async def mvp(interaction: discord.Interaction):
            await self.command_handler.handle_mvp(interaction)

        @self.tree.command(name="今北産業", description="過去の100投稿を3行にまとめる")
        async def imakita(interaction: discord.Interaction):
            await self.command_handler.handle_imakita(interaction)

        @self.tree.command(name="silent要約", description="要約結果をあなただけにお届け")
        async def silent_summarize(interaction: discord.Interaction):
            await self.command_handler.handle_summary(interaction, silent=True)

        @self.tree.command(name="silent_mvp", description="mvpをあなただけにお届け")
        async def silent_mvp(interaction: discord.Interaction):
            await self.command_handler.handle_mvp(interaction, silent=True)

        @self.tree.command(name="silent今北産業", description="過去の100投稿を3行にまとめてあなただけにお届け")
        async def silent_imakita(interaction: discord.Interaction):
            await self.command_handler.handle_imakita(interaction, silent=True)

        @self.tree.command(name="vc参加", description="BOTをVCに参加させます")
        async def join(interaction: discord.Interaction):
            await self.command_handler.handle_voice_join(interaction)

        @self.tree.command(name="vc退出", description="BOTをVCから退出させます")
        async def leave(interaction: discord.Interaction):
            await self.command_handler.handle_voice_leave(interaction)

        @self.tree.command(name="性格分析mbti", description="過去の投稿から性格を分析")
        async def mbti(interaction: discord.Interaction):
            await self.command_handler.handle_personality_analysis(interaction, "MBTI")

        @self.tree.command(name="silent性格分析mbti", description="過去の投稿から性格を分析して、あなただけにお届け")
        async def silent_mbti(interaction: discord.Interaction):
            await self.command_handler.handle_personality_analysis(interaction, "MBTI", silent=True)

        @self.tree.command(name="性格分析big5", description="過去の投稿から性格を分析")
        async def big5(interaction: discord.Interaction):
            await self.command_handler.handle_personality_analysis(interaction, "BIG5")

        @self.tree.command(name="silent性格分析big5", description="過去の投稿から性格を分析して、あなただけにお届け")
        async def silent_big5(interaction: discord.Interaction):
            await self.command_handler.handle_personality_analysis(interaction, "BIG5", silent=True)

        @self.tree.command(name="年齢推定", description="過去の投稿から年齢を推定")
        async def age_guess(interaction: discord.Interaction):
            await self.command_handler.handle_age_estimation(interaction)

        @self.tree.command(name="silent年齢推定", description="過去の投稿から年齢を推定して、あなただけにお届け")
        async def silent_age_guess(interaction: discord.Interaction):
            await self.command_handler.handle_age_estimation(interaction, silent=True)

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Command tree synced")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user}')

    async def on_voice_state_update(self, member, before, after):
        voice_channel = None
        for vc in self.voice_clients:
            if vc.guild == member.guild:
                voice_channel = vc.channel
                break

        if voice_channel and len(voice_channel.members) == 1 and voice_channel.members[0] == self.user:
            await self.voice_clients[0].disconnect()
            logger.info("Bot left voice channel as it was the only member remaining")

    async def on_message(self, message):
        try:
            if message.author.bot:
                return

            guild_id = message.guild.id
            if (guild_id not in self.command_handler.selected_text_channel or 
                self.command_handler.selected_text_channel[guild_id] != message.channel.id):
                return

            vc = message.guild.voice_client
            if not vc:
                return

            text = self.message_cleaner.clean_text(message.content.strip())
            await self.command_handler.tts_service.text_to_speech(text, vc)

        except Exception as e:
            logger.error(f"Error in message handling: {e}")
