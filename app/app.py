from discord import Intents
from discord.ext import commands

TOKEN = "ODU2NTg0NTE0NTg2NTQyMDkw.GNhESR.ThmjfDeOMWwoDRR8SW48vRUaJcQlGACRPJB_YQ" # This is temporary.

intents = Intents.default()
intents.message_content = True
bot = commands.Bot("!", intents=intents)


@bot.command()
async def foo(context, *arguments):
    await context.send(arguments)


bot.run(TOKEN)
