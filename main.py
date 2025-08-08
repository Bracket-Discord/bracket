from core.bracket import BracketBot
from configs import settings


bot = BracketBot()
bot.run(settings.bot_token)
