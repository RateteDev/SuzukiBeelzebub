from google.generativeai import GenerativeModel, configure
import discord
import logging

logger = logging.getLogger('discord_bot')

class GeminiService:
    def __init__(self, api_key):
        configure(api_key=api_key)
        self.model = GenerativeModel("gemini-1.5-pro")
        logger.info("Gemini AI service initialized")

    async def summarize(self, text, title, prompt_prefix=""):
        try:
            prompt = f"{prompt_prefix}次の文章を要約してください：\n{text}"
            response = self.model.generate_content(prompt)
            
            embed = discord.Embed(
                title=title,
                description=response.text,
                color=0x00ff00
            )
            return embed
        except Exception as e:
            logger.error(f"Error in Gemini summarization: {e}")
            raise

    async def analyze_personality(self, text, user_name, analysis_type):
        try:
            prompt = f"次の文章({user_name}の発言)を{analysis_type}で分析してください：\n{text}"
            response = self.model.generate_content(prompt)
            
            embed = discord.Embed(
                title=analysis_type,
                description=response.text,
                color=0x00ff00
            )
            return embed
        except Exception as e:
            logger.error(f"Error in personality analysis: {e}")
            raise

    async def analyze_age(self, text, user_name):
        try:
            prompt = f"次の文章({user_name}の発言)から精神年齢と実年齢を推定してください：\n{text}"
            response = self.model.generate_content(prompt)
            
            embed = discord.Embed(
                title="年齢推定結果",
                description=response.text,
                color=0x00ff00
            )
            return embed
        except Exception as e:
            logger.error(f"Error in age analysis: {e}")
            raise
