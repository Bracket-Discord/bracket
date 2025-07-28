import discord
from discord.ext import commands
from config import settings

import cogs


class Bot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("jishaku")
        for ext in cogs.values:
            try:
                await self.load_extension(f"cogs.{ext}")
            except Exception as e:
                print(f"Failed to load {ext} cog: {e}")

        await bot.tree.sync(guild=discord.Object(id=settings.default_guild_id))
        print("Bot setup complete.")

    async def is_owner(self, user: discord.abc.User, /) -> bool:
        if user.id in settings.owner_ids:
            return True
        return await super().is_owner(user)


if __name__ == "__main__":
    bot = Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.default())
    bot.run(settings.bot_token)
