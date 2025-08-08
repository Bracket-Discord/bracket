import discord
from discord.ext import commands
from core.bracket import BracketBot
from configs import settings


bot = BracketBot(
    command_prefix=commands.when_mentioned, intents=discord.Intents.default()
)
bot.run(settings.bot_token)
