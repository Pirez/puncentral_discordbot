# bot.py
import os
import sys
import json
import random

from loguru import logger
from dotenv import load_dotenv
from faceit import FaceitData
from discord.ext import commands

fd = FaceitData()
load_dotenv(override=True)
bot = commands.Bot(command_prefix='!')

@bot.command(name='lvl', help='Get lvl stat, example: !lvl Stutmunn or !lvl all')
async def get_stat_faceit(ctx, username):
    usernames = json.loads(os.environ['USERNAMES'])
    if len(usernames) == 0:
        logger.error("Please define a set of usernames in `.env`!")
        return None

    emojis = {1: "🤮", 2: "💩", 3: "😀", 4: "😈", 5: "🎖", 6: "🥷", 7: "🤴🏻", 8: "🥇", 9: "🥇", 10: "🥇"}

    if username == "all":
        data = {}

        for username in usernames:
            stat = fd.get_userstat(username)
            level = stat['items'][0]['games'][0]['skill_level']
            data[username] = level
        
        data = sorted(data, key=data.get, reverse=True)
        output_txt = [f"**{user}** Level {level} {emojis[int(level)]}" for user, level in data.items()]
        output_txt = "\n".join(output_txt)
        await ctx.send(output_txt)

    else:
        stat = fd.get_userstat(username)
        level = stat['items'][0]['games'][0]['skill_level']
        response = f"**{username.capitalize()}** Level {emojis[int(level)]}"
        await ctx.send(response)


@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    """ Just an example """
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


discord_token = os.getenv("DISCORD_TOKEN", None)
if discord_token is None:
    logger.error("Did not provide DISCORD bot token, exiting!")
    sys.exit(1)

logger.info("Started up PunCentralBot...")
bot.run(discord_token)