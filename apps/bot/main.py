from configs import settings
from core.bot import BracketBot

bot = BracketBot()
bot.run(settings.bot_token)
