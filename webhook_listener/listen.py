from distutils.log import debug
import os
import time
import numpy as np
import requests

from loguru import logger
from dotenv import load_dotenv
from flask import Flask,request,json, Response

from faceit import FaceitData


load_dotenv(override=True)
_debug = os.getenv("DEBUG", False)
app = Flask(__name__)
error_login = Response("{'Login':'Error'}", status=401, mimetype='application/json')


def send_message_to_discordchannel(message: str, channelid: int):
    """
    Post a direct message to a Discord Channel    
    """
    botToken = os.getenv("DISCORD_TOKEN", None)

    baseURL = f"https://discordapp.com/api/channels/{channelid}/messages"
    headers = { "Authorization":f"Bot {botToken}",
                "User-Agent":"punCentralBot (http://puncentr.al, v1.0)",
                "Content-Type":"application/json", }

    POSTedJSON =  json.dumps ( {"content": message} )
    r = requests.post(baseURL, headers = headers, data = POSTedJSON)


def _simple_security(args, headers):
    """ Check query/header for a token """
    if "csgo" in args and args['csgo'] == os.getenv("QUERY_TOKEN", None):
        if headers.get('token_secret') and headers['token_secret'] == os.getenv("WEBHOOK_SECRET_TOKEN", None):
            return True
    return False


def find_next_level(elo_x):
    elo_ranking = np.array([0, 800, 950, 1100, 1250, 1400, 1550, 1700, 1850, 2000])
    diff_elo = elo_ranking[elo_x-elo_ranking < 0][0] - elo_x
    level = sum(elo_x-elo_ranking > 0) + 1
    return level, diff_elo



def post_match_ready(data):

    """ . """
    fd = FaceitData()
    gamesids = json.loads(os.environ['GAMERIDS'])
    
    team_idx = 1
    valid_players_in_game = {z['game_id']: z['game_name'] for z in data['payload']['teams'][0]['roster'] if z['game_id'] in gamesids}
    if len(valid_players_in_game) == 0:
        valid_players_in_game = {z['game_id']: z['game_name'] for z in data['payload']['teams'][1]['roster'] if z['game_id'] in gamesids}
        team_idx = 0
    logger.warning(f"{len(valid_players_in_game)} valid_players_in_game")

    elo_stat = {}
    for gid, username in valid_players_in_game.items():
        elo_x = fd.get_userstat_gamerid(gid)['games']['csgo']['faceit_elo']
        elo_stat[username] = elo_x

    output_txt = [f"**MATCH is READY** against **{data['payload']['teams'][team_idx]['name']}** 😎\n"]
    limit_elo = 30
    limit_elo_min = 10_000
    for username, elo in elo_stat.items():
        lvl, diff_elo = find_next_level(elo)

        if username == 'Stutmunn' and diff_elo < limit_elo:
            output_txt.append(f"🚨 **OMG** 🚨 *{username.capitalize().strip()}* can ACTUALLY level up to **{lvl}** if we win 🤯 (missing {diff_elo} ELO!)")
        elif diff_elo < limit_elo:
            output_txt.append(f"*{username.capitalize().strip()}* can level up to **{lvl}** if we win 🤩 (missing {diff_elo} ELO!)")
        
        # Check the user which is cloest to rank up
        if diff_elo < limit_elo_min:
            limit_elo_min = diff_elo
            closest_username = username
            cloest_elo = diff_elo
            
    if len(output_txt) == 1:
        output_txt = output_txt[0]
        output_txt += f"If we win the match, nobody will rank up 🥱 \nBut the closest user to rank up, is *{closest_username}* (missing {cloest_elo} ELO) 🤠"
    else:
        output_txt = "\n".join(output_txt)   

    channelid = os.getenv("CHANNEL_ID", None)
    logger.info(channelid)
    #channelid = "934828226507841620"
    send_message_to_discordchannel(output_txt, channelid)


@app.route('/')
def main():
    data = request.json
    args, headers = request.args.to_dict(), request.headers
    checkStatus = _simple_security(args, headers)

    if checkStatus:
        return 'Ok!'
    return error_login


def get_finished_match_stat(matchid: str):
    """ . """
    fd = FaceitData()
    stat_match = fd.get_match_stat(matchid)
    playerids = json.loads(os.environ['PLAYERIDS'])

    _map = stat_match['rounds'][0]['round_stats']['Map']
    _score = stat_match['rounds'][0]['round_stats']['Score']

    map_emoji = {'de_nuke': '☢️', 
                 'de_dust2': '🌵', 
                 'de_mirage': '🏜️', 
                 'de_overpass': '🧺',
                 'de_ancient': '🗿', 
                 'de_train': '🚂',
                 'de_vertigo': '🏢'}

    _map += f" {map_emoji[_map] if _map in map_emoji else '💣'}"

    winner_team = stat_match['rounds'][0]['round_stats']['Winner']
    txt = ""#5"0*"-" + "\n""
    txt += f"Match finished: **{_map}** \n" 
    txt += "```"
    txt += f"  {'':15} | {'Kills':7} | {'Deaths':7} | {'Assists':7} | {'MVPs':7} | {'3/4/5 kills'}\n"

    for t in stat_match['rounds'][0]['teams'][::-1]:
        winning_team = winner_team == t['team_id']
        players_ = [i for i in t["players"] if i['player_id'] in playerids]
        if len(players_) > 1:
            for p in players_:
                nickname = p['nickname']
                
                stuff = ''
                
                tri_kills = int(p['player_stats']['Triple Kills'])
                qu_kills = int(p['player_stats']['Quadro Kills'])
                pe_kills = int(p['player_stats']['Penta Kills'])
                if  tri_kills > 0:
                    stuff += "🔫"
                if qu_kills  > 0:
                    stuff += "🔥"
                if pe_kills > 0:
                    stuff += "💯"
                
                kd_ratio = '+' if float(p['player_stats']['K/D Ratio']) >= 1 else '-'
                
                txt += f"{kd_ratio} {nickname.strip():15} | {p['player_stats']['Kills']:7} | {p['player_stats']['Deaths']:7} | {p['player_stats']['Assists']:7} | {p['player_stats']['MVPs']:7} | {stuff}\n"
        else:
            other_team = t['team_stats']['Team']

    txt += "```"    
    if winning_team and len(players_) > 1:
        txt += f" 🥳 Won {_score} Rounds against **{other_team}**"
    else:
        txt += f" 😭 Lost {_score} Rounds against **{other_team}**"
    channelid = os.getenv("CHANNEL_ID", None)
    logger.info(channelid)

    send_message_to_discordchannel(txt, channelid)


@app.route('/api', methods=['POST'])
def puncentral_listen():
    data = request.json
    args, headers = request.args.to_dict(), request.headers
    checkStatus = _simple_security(args, headers)

    
    if checkStatus:
        if _debug:
            output_file = data['event'].lower().replace(" ", "_")
            logger.debug(f"Dumping data, {output_file}")
            with open(f'{output_file}_{int(time.time())}.json', 'w') as outfile:
                json.dump(json.dumps(data), outfile)

        if data['event'] == "match_status_ready":
            post_match_ready(data)
        elif data['event'] == "match_status_finished":
            get_finished_match_stat(data['payload']['id'])
        else:
            txt = f"🤖 - Event detected, **{data['event']}**!"
            #send_message_to_discordchannel(txt, channelid)

        return data
    return error_login


if __name__ == '__main__':
    app.run(debug=_debug, host="localhost", port=5001)