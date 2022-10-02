import os
import uuid

import boto3
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.message_content = True
bot = commands.Bot("!", intents=intents)


@bot.command()
async def ping(context, *args):
    await context.send("pong")


@bot.command()
async def create_milestone(context, *args):
    table = boto3.resource("dynamodb", region_name="us-west-1").Table("Milestones")

    table.put_item(
        TableName="Milestones",
        Item={
            "MilestoneId": str(uuid.uuid4()),
            "Date": args[0],
            "Text": " ".join(args[1:]),
            "AuthorId": context.author.id,
        },
    )

    await context.send("success")


bot.run(os.environ["BOT_TOKEN"])
