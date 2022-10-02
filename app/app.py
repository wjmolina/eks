import os
import uuid
from bisect import insort
from collections import defaultdict

import boto3
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot("!", intents=intents)

milestones_table = boto3.resource("dynamodb", region_name="us-west-1").Table("Milestones")
milestones_channel = 1025250447847587870


@bot.command()
async def ping(ctx, *args):
    await ctx.send("pong")


@bot.command()
async def create_milestone(ctx, *args):
    milestones_table.put_item(
        TableName="Milestones",
        Item={
            "MilestoneId": str(uuid.uuid4()),
            "Date": args[0],
            "Text": " ".join(args[1:]),
            "AuthorId": ctx.author.id,
        },
    )

    await ctx.send("success")

    data = defaultdict(list)

    for item in milestones_table.scan()["Items"]:
        insort(data[item["AuthorId"]], [item["Date"], item["Text"]])

    milestones_message = ""

    for author_id, milestones in data.items():
        milestones_message += bot.get_user(author_id).mention + "\n"
        milestones_message += "```\n"

        for date, text in milestones:
            milestones_message += f"{date}: {text}\n"

        milestones_message += "```\n"

    await bot.get_channel(milestones_channel).send(milestones_message)


bot.run(os.environ["BOT_TOKEN"])
