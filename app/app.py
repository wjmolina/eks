import os

from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.message_content = True
bot = commands.Bot("!", intents=intents)


@bot.command()
async def foo(context, *arguments):
    await context.send(arguments)


bot.run(os.environ["BOT_TOKEN"])
