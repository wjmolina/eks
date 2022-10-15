import os
import uuid
from bisect import insort
from collections import defaultdict
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Attr
from discord import Intents
from discord.ext.commands import Bot, Parameter

from connect_four import get_is_game_over_winner, make_move, pos_to_board, visualize_board

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = Bot("!", intents=intents)

milestones_table = boto3.resource("dynamodb", region_name="us-west-1").Table("Milestones")
connect_four_table = boto3.resource("dynamodb", region_name="us-west-1").Table("ConnectFour")

milestones_channel_id = 1025250447847587870


def create_milestones_content():
    data = defaultdict(list)

    for item in milestones_table.scan()["Items"]:
        insort(data[item["AuthorId"]], [item["MilestoneId"], item["Date"], item["Text"]])

    milestones_message = ""

    for author_id, milestones in sorted(data.items()):
        milestones_message += bot.get_user(author_id).mention + "\n"
        milestones_message += "```\n"

        for milestone_id, date, text in milestones:
            date = datetime.strptime(date, "%Y-%m-%d")
            if (datetime.now() - date) < timedelta(days=7):
                milestones_message += f"{milestone_id} | {date.strftime('%b %d, %Y')} | {text}\n"

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
    brief="Create a milestone.",
    help="Given a date and some text, this command will update the message in the milestones channel with this information.",
)
async def create_milestone(
    ctx,
    date=Parameter("date", Parameter.POSITIONAL_OR_KEYWORD, description="YYYY-MM-DD"),
    text=Parameter("text", Parameter.VAR_POSITIONAL, description="Write your milestone here in quotes."),
):
    singleton = await create_or_read_channel_singleton(milestones_channel_id)
    datetime.strptime(date, "%Y-%m-%d")
    milestones_table.put_item(
        Item={
            "MilestoneId": str(uuid.uuid4()),
            "Date": date,
            "Text": text,
            "AuthorId": ctx.author.id,
        }
    )
    await singleton.edit(content=create_milestones_content())
    await ctx.send("success")


@bot.command(
    brief="Delete a milestone.",
    help="Given a milestone ID, this command will delete the associated milestone.",
)
async def delete_milestone(
    ctx,
    id=Parameter("id", Parameter.POSITIONAL_OR_KEYWORD, description="Milestone ID"),
):
    singleton = await create_or_read_channel_singleton(milestones_channel_id)
    milestones_table.delete_item(Attr={"MilestoneId": id})
    await singleton.edit(content=create_milestones_content())
    await ctx.send("success")


@bot.command(
    brief="Play Connect Four.",
    help="Play Connect Four against an AI that taught itself in a few hours.",
)
async def connect_four(
    ctx,
    move=Parameter("move", Parameter.POSITIONAL_OR_KEYWORD, description="a number from 1 to 7 representing the column"),
):
    def get_items():
        return connect_four_table.scan(FilterExpression=Attr("PlayerId").eq(ctx.author.id) & Attr("IsGameOver").eq(False))["Items"]

    items = get_items()

    if not items:
        connect_four_table.put_item(
            Item={
                "GameId": str(uuid.uuid4()),
                "PlayerId": ctx.author.id,
                "Position": "",
                "IsGameOver": False,
                "Date": str(datetime.utcnow()),
            }
        )
        items = get_items()

    item = items[0]

    if move.lower() == "forfeit":
        item["IsGameOver"] = True
    else:
        item["Position"] = make_move(item["Position"], move)
        board = pos_to_board(item["Position"])
        await ctx.send(visualize_board(board))
        item["IsGameOver"] = get_is_game_over_winner(board)[0]

    connect_four_table.put_item(Item=item)


bot.run(os.environ["BOT_TOKEN"])
