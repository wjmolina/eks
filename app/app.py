import os
import uuid
from bisect import insort
from collections import defaultdict
from datetime import datetime

import boto3
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot("!", intents=intents)

milestones_table = boto3.resource("dynamodb", region_name="us-west-1").Table("Milestones")
milestones_channel_id = 1025250447847587870


def create_milestones_message():
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

    return milestones_message


async def create_or_get_channel_singleton(channel_id):
    channel = bot.get_channel(channel_id)
    has_skipped_one = False
    single_message = None

    async for message in channel.history():
        if not has_skipped_one:
            single_message = message
            has_skipped_one = True
            continue

        message.delete()

    if not single_message:
        single_message = await channel.send("placeholder")

    return single_message


@bot.command()
async def ping(ctx, *args):
    await ctx.send("pong")


@bot.command()
async def create_milestone(ctx, *args):
    singleton = await create_or_get_channel_singleton(milestones_channel_id)
    datetime.strptime(args[0], "%Y-%m-%d")
    milestones_table.put_item(
        TableName="Milestones",
        Item={
            "MilestoneId": str(uuid.uuid4()),
            "Date": args[0],
            "Text": " ".join(args[1:]),
            "AuthorId": ctx.author.id,
        },
    )
    message = create_milestones_message()
    await singleton.edit(content=message)
    await ctx.send("success")


bot.run(os.environ["BOT_TOKEN"])
