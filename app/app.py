import os
import uuid
from bisect import insort
from collections import defaultdict
from datetime import datetime, timedelta

import boto3
from discord import Intents
from discord.ext import commands

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot("!", intents=intents)

milestones_table = boto3.resource("dynamodb", region_name="us-west-1").Table("Milestones")
milestones_channel_id = 1025250447847587870


def create_milestones_content():
    data = defaultdict(list)

    for item in milestones_table.scan()["Items"]:
        insort(data[item["AuthorId"]], [item["Date"], item["Text"]])

    milestones_message = ""

    for author_id, milestones in sorted(data.items()):
        milestones_message += bot.get_user(author_id).mention + "\n"
        milestones_message += "```\n"

        for date, text in milestones:
            date = datetime.strptime(date, "%Y-%m-%d")
            if (datetime.now() - date) < timedelta(days=7):
                milestones_message += f"{date.strftime('%b %d, %Y')}: {text}\n"

        milestones_message += "```\n"

    return milestones_message


async def create_or_read_channel_singleton(id):
    channel = bot.get_channel(id)
    has_skipped_one = False
    singleton = None

    async for message in channel.history():
        if not has_skipped_one:
            singleton = message
            has_skipped_one = True
            continue

        message.delete()

    if not singleton:
        singleton = await channel.send("placeholder")

    return singleton


@bot.command(
    **{
        "brief": "Create a milestone.",
        "description": "Given a date and some text, this command will update the message in the milestones channel with this information.",
    }
)
@bot.describe(
    date="YYYY-MM-DD",
    text="text",
)
async def create_milestone(ctx, date, *text):
    singleton = await create_or_read_channel_singleton(milestones_channel_id)
    datetime.strptime(date, "%Y-%m-%d")
    milestones_table.put_item(
        TableName="Milestones",
        Item={
            "MilestoneId": str(uuid.uuid4()),
            "Date": date,
            "Text": " ".join(text[1:]),
            "AuthorId": ctx.author.id,
        },
    )
    content = create_milestones_content()
    await singleton.edit(content=content)
    await ctx.send("success")


bot.run(os.environ["BOT_TOKEN"])
