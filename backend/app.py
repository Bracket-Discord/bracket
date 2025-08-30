from fastapi import FastAPI
from core.bracket import bot

app = FastAPI()


@app.get("/guilds")
async def get_guilds():
    return [{"id": guild.id, "name": guild.name} for guild in bot.guilds]
