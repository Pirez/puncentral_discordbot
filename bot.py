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

    emojis = {1: "🤮", 2: "💩", 3: "😐", 4: "😁", 5: "🎖", 6: "🥷 ", 7: "🤴🏻", 8: "🥇", 9: "🥇", 10: "🥇"}

    if username == "all":
        data = {}

        for username in usernames:
            stat = fd.get_userstat(username)
            skill_level = stat['games']['csgo']['skill_level']
            elo = stat['games']['csgo']['faceit_elo']
            data[username] = {"lvl": skill_level, "elo": elo}
        
        output_txt = [f" {emojis[int(d['lvl'])]} - {user.capitalize()} Level: **{d['lvl']}** (*{d['elo']}*)" for user, d in data.items()]
        output_txt = "\n".join(output_txt)
        await ctx.send(output_txt)

    else:
        stat = fd.get_userstat(username)
        level = stat['items'][0]['games'][0]['skill_level']
        response = f"**{username.capitalize()}** Level {level} {emojis[int(level)]}"
        await ctx.send(response)

@bot.command(name='stat', help='Get fun stats!')
async def get_stat_faceit(ctx):
    playerids = json.loads(os.environ['PLAYERIDS'])
    usernames = json.loads(os.environ['USERNAMES'])

    if len(playerids) == 0 or len(usernames) == 0:
        logger.error("Please define a set of playerids/usernames in `.env`!")
        return None

    emojis = {1: "🤮", 2: "💩", 3: "😐", 4: "😁", 5: "🎖", 6: "🥷 ", 7: "🤴🏻", 8: "🥇", 9: "🥇", 10: "🥇"}

    mapping_usernames = {uname: pid for uname, pid in zip(usernames, playerids)}

    data = {}

    for uname, pid in mapping_usernames.items():
        stat = fd.get_funstat(pid)
        avg_winrate = stat['lifetime']['Win Rate %']
        longest_winstreak = stat['lifetime']['Longest Win Streak']
        current_winstreak = stat['lifetime']['Current Win Streak']
        avg_kd = stat['lifetime']['Average K/D Ratio']
        avg_headshots = stat['lifetime']['Average Headshots %']
        data[uname] = {"kd": avg_kd, 
                            "hd": avg_headshots,
                            "lw": longest_winstreak,
                            "cw": current_winstreak,
                            "wr": avg_winrate,
                            "avg_headshots": avg_headshots}

    output_txt = [f"*{user.capitalize().strip()}*: Winstreak (current/record): **{d['cw']}/{d['lw']}**  -  K/D: **{d['kd']}** - Headshots **{d['hd']}%** - Winrate **{d['wr']}%**"  for user, d in data.items()]
    output_txt = "\n".join(output_txt)
    await ctx.send(output_txt)


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
