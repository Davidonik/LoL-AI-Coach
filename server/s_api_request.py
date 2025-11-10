import os
import json
import boto3
import requests
import markdown
from pathlib import Path
from flask_cors import CORS
from markupsafe import Markup
from flask import Flask, request, jsonify, make_response, redirect, url_for, render_template, session

# API Key for LoL
APIKEY_LOL = "RGAPI-d7903387-6d1e-4d07-88a1-6763cfebacee"

# Bedrock Model Configs
BEDROCK = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
MODEL_ID = "arn:aws:bedrock:us-east-1:085366697379:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"

# AI Prompt Bases
BASE = (
    "You are a Challenger-ranked League of Legends coach with over 10 years of competitive and analytical experience. " 
    "Your tone is confident, encouraging, and professional — like a high-ELO coach reviewing a player's match history. " 
    "You focus on actionable, measurable advice with in-game reasoning (timing, wave control, map awareness, etc.). " 
    "Use game-specific vocabulary correctly (e.g., roam timings, CS@10, lane priority, objective control, tempo, macro). " 
    "Avoid fluff or generic comments. Always explain why each issue matters in terms of win conditions and map state." 
    "When data is unclear, infer gently — never guess random numbers. " 
    "Keep answers concise and structured. "
)

#######################################################
###################### FLASH APP ######################
#######################################################

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = "some_secret_key"

CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    games = get_last20gamesstuff()
    if games == None:
        games = []
    return render_template("dashboard.html", ign=f"{request.cookies.get("sname")}#{request.cookies.get("tag")} ", games=games)

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/review")
def review():
    stats = session.get("match_data", [])
    coach_response = session.get("coach_response", None)
    html_response = markdown.markdown(coach_response, extensions=["fenced_code", "tables"])
    
    return render_template("review.html", coach_response=(html_response), stats=stats, ign=f"{request.cookies.get("sname")}#{request.cookies.get("tag")} ")

@app.route("/api/leaderboard", methods=["GET"])
def load_leaderboard():
    leaderboardRankings = get_leaderboard("kda", False) # still need sort key and order of sort asc(true) or desc(false)
    if None == leaderboardRankings:
        return make_response(jsonify({"error": f"No player was defined"}))
    return make_response(jsonify(leaderboardRankings))

@app.route("/api/set_user", methods=["POST"])
def set_user():
    data = request.get_json()
    sname = data.get("sname", None)
    tag = data.get("tag", None)
    
    # no sname or tag given in fetch
    if None == sname or None == tag:
        return make_response(jsonify({"error": "invalid summoner name and/or tag"}))
    
    # make requests to LoL API 
    puuid = lolapi_puuid(sname, tag)
    if None == puuid:
        return make_response(jsonify({"error": f"summoner not found"}))

    # Create a redirect response (to some route, e.g. /dashboard)
    response = make_response(redirect(url_for("dashboard")))
    
    response.set_cookie("sname", sname, max_age=60*60*24)
    response.set_cookie("tag", tag, max_age=60*60*24)
    response.set_cookie("puuid", puuid, max_age=60*60*24)
    return response

@app.route("/api/player/stats", methods=["GET"])
def get_player_stats():
    playerData = get_playerData(request.cookies.get("puuid", None))
    if None == playerData:
        return make_response(jsonify({"error": f"No player was defined"}))
    return make_response(jsonify(playerData))

@app.route("/aws/ai_traits", methods=["POST"])
def ai_traits():
    # Get stats for player
    playerData = get_playerData(request.cookies.get("puuid", None))
    traits = playerData["traits_"].keys()
    del playerData["traits_"]
    
    # AI Prompt Creation
    prompt = (
        f"{BASE} The following is your student's statistics from past reviews in json format:\n"
        f"{str(playerData)}\n"
        "Summarize the player into traits by making in a json object using the follow keys, keep the values to be one word:\n"
        f"{str(traits)}"
    )
    
    # AWS Request Structure
    body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "anthropic_version": "bedrock-2023-05-31",
    }

    # Send the request to AWS Bedrock
    aws_response = BEDROCK.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    aws_response_body = json.loads(aws_response["body"].read())
    
    response = make_response(jsonify({
        "message": True,
        "ai_response": aws_response_body["content"][0]["text"]
    }))
    
    return response

@app.route("/aws/ai_coach", methods=["POST"])
def ai_coach():
    data = request.get_json()
    matchid = data.get("matchid")
    roasting = data.get("roast")
    match_data = get_matchdata(matchid)
    opponent_puuid = parse_player_opponent(match_data, request.cookies.get("puuid"))["opponentpuuid"]

    player_stats = get_playerstatsAt10(matchid, request.cookies.get("puuid"))
    opponent_stats = get_playerstatsAt10(matchid, opponent_puuid)
    champion_data = get_champdata(matchid)

    # AI Prompt Creation
    context = (
        f"""
        You are reviewing a player's recent ranked game. The following data is provided:\n
        {match_data}\n
        {champion_data}\n
        The information about the player you are coaching {player_stats}.\n
        The information about the player's lane opponent {opponent_stats}.\n
        At 10 minutes, Miss Fortune has 4295 gold and Xayah has 3458 gold. 
        Miss Fortune has 75 cs and Xayah has 57 cs. 
        Miss Fortune has a 5.0 KDA and Xayah has a 0.75 KDA. 
        Focus on laning phase performance — last-hitting, positioning, early wave control trading with opponents.\n
        """
    )

    task = (
        """
        Identify the lane result, whether the player ended up behind, even, or ahead of the opposing laner at the 10 minute mark based on the player's gold, level, and KDA. 
        Next identify the top 2-3 mistakes in the laning phase and explain how they affected the player's result at the 10 minute mark. 
        Then provide 2 actionable coaching tips with clear timings or cues (e.g., 'At 3:15 when wave 3 crashes…'). \n
        """
    )

    roast = (
        """
        The roast button is on !!!, On top of the prompt above be as brutally honest as you can. Make fun of the player when you get the chance.\n
        The roast should be 2 to 3 sentence flame session describing how bad or surprisingly decent the player was.\n
        Tone:\n
        Ruthlessly honest, witty, and slightly toxic—but never truly mean or insulting.\n
        Think of a Challenger coach who’s tired of Bronze mistakes but still wants you to climb.\n
        Use short, punchy sentences. Drop a joke or two if it fits.\n
        Always balance the roast with an actual coaching point (e.g., “You died level 3 to a jungle gank—maybe try warding before inting next time.")\n
        """
    )

    if roasting == True:
        prompt = f"{BASE} {context} {task} {roast}"
    else:
        prompt = f"{BASE} {context} {task}"


    # AWS Request Structure
    body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "anthropic_version": "bedrock-2023-05-31",
    }

    # Send the request to AWS Bedrock
    aws_response = BEDROCK.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    # The response body comes as a byte stream, so decode it:
    aws_response_body = json.loads(aws_response["body"].read())
    coach_response = aws_response_body["content"][0]["text"]
    
    session["coach_response"] = coach_response
    session["match_data"] = match_data
    
    return redirect(url_for("review"))

@app.route("/api/get_matches", methods=["POST"])
def getLast20Matches():
    puuid = request.cookies.get("puuid", None)
    if None == puuid:
        return make_response(jsonify({"error": "summoner not found"}))
    return lolapi_matches(puuid)

@app.route("/api/player/update_stats", methods=["POST"])
def update_stats():
    data = request.get_json()
    matchid = data.get("matchid", None)
    current_stats = get_playerData(request.cookies.get("puuid", None))
    new_stats = get_stats_to_save(matchid, request.cookies.get("puuid", None))
    
    if matchid in current_stats["reviewed_matchids"]:
        return make_response(jsonify({"message": "already reviewed this game"}))
    
    # Update stats then write to file
    KDA_ = current_stats["KDA_"]
    new_KDA_ = new_stats["KDA_"]
    total_ = current_stats["total_"]
    new_total_ = new_stats["total_"]
    
    for key in KDA_.keys():
        KDA_[key] += new_KDA_[key]
        
    for key in total_.keys():
        total_[key] += new_total_[key]
        
    if new_stats["firstBloodKill"]:
        current_stats["firstBloodKill"] += 1
    
    total_obj_killed = 0
    for obj in new_stats["objectives"].keys():
        total_obj_killed += (new_stats["objectives"][obj]["kills"] if obj != "champion" and obj != "tower" and obj != "inhibitor" else 0)
    current_stats["objectives"] += total_obj_killed
    
    last20matchids = lolapi_matches(request.cookies.get("puuid", None))

    # Keep only reviewed matches that are still in the last 20
    current_stats["reviewed_matchids"] = [
        mid for mid in current_stats["reviewed_matchids"] if mid in last20matchids
    ]

    current_stats["reviewed_matchids"].append(matchid)

    with open("./playerData/playerData.json", "w") as file:
        json.dump(current_stats, file, indent=4)
    
    return make_response(jsonify({"message": "update complete"}))
    

##############################################################
###################### LoL API REQUESTS ######################
##############################################################

def lolapi_puuid(sname: str, tag: str) -> str:
    """_summary_

    Args:
        sname (str): summoner name
        tag (str): tagline of summoner

    Returns:
        str: corresponding summoner's PUUID
    """
    # Player Info
    api_request = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{sname}/{tag}?api_key={APIKEY_LOL}"
    resp = requests.get(api_request)
    
    if resp.status_code != 200:
        return None
    
    return resp.json()["puuid"]

def lolapi_matches(puuid: str) -> list:
    """_summary_

    Args:
        puuid (str): player's PUUID

    Returns:
        list: list of match ids 
        None: errors return None
    """
    api_url_matches = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={APIKEY_LOL}"
    resp = requests.get(api_url_matches)
    
    if resp.status_code != 200:
        return None
    
    first20matches = resp.json()
    return first20matches

##############################################################
###################### PARSER FUNCTIONS ######################
##############################################################

def parse_traits(playerData: dict) -> list:
    """_summary_

    Args:
        playerData (dict): player data object from player sheet

    Returns:
        list: key value pair of all player traits
    """
    return [(key, playerData["traits_"][key]) for key in dict(playerData["traits_"]).keys()]

def parse_player_opponent(matchdata: dict, puuid: str):
    """_summary_

    Args:
        matchdata (dict): data of matches 
        puuid (str): player's PUUID

    Returns:
        dict: player -> player's match data, opponent -> lane opponent's match data
        None: errors return None
    """
    if None == matchdata or None == puuid:
        return None

    playerindex = matchdata["metadata"]["participants"].index(puuid)
    opponentindex = (playerindex + 5) % 2
    opponentpuuid = matchdata["metadata"]["participants"][opponentindex]

    player = matchdata["info"]["participants"][playerindex]
    opponent = matchdata["info"]["participants"][opponentindex]
    
    return {
        "player": player,
        "opponent": opponent,
        "opponentpuuid": opponentpuuid
    }

#############################################################
####################### GET FUNCTIONS #######################
#############################################################

def get_matchdata(matchid: str) -> dict:
    """_summary_

    Args:
        matchid (str): match id of the chosen match.

    Returns:
        dict: full data on the match
    """
    api_url_match = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={APIKEY_LOL}"
    resp = requests.get(api_url_match)
    matchdata = resp.json()

    return matchdata

def get_champdata(matchid: str ,folderpath="champions") -> dict:
    """_summary_

    Args:
        matchid (str): id of specific match
        folderpath (str, optional): path to champion data dir. Defaults to "champions".

    Returns:
        dict: data on champions
    """
    championdata = {}
    matchdata = get_matchdata(matchid)

    # Champions for the specific match
    for i in range(0, 10):
        championname = matchdata["info"]["participants"][i]["championName"]
        filename = f"{championname}.json"
        filepath = os.path.join(folderpath, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as champdata:
                championdata[championname] = json.load(champdata)
        except FileNotFoundError:
            championdata[championname] = {"error": f"{championname}.json not found"}

    return championdata

def get_participant_index(matchdata: dict, puuid: str) -> int | None:
    """_summary_

    Args:
        matchdata (dict): match data of the chosen match.
        puuid (str): player's id for query

    Returns:
        int: Returns the participant index (0 to 9) for a given player's PUUID.
    """
    for i, p in enumerate(matchdata["info"]["participants"]):
        if p["puuid"] == puuid:
            return i
    return None

def get_stats(matchdata: dict) -> dict:
    """_summary_

    Args:
        matchdata (dict): match data of the chosen match.

    Returns:
        dict: returns the stats of the player
    """
    queuetypebyid = {
        420: "Ranked", 
        440: "Ranked Flex", 
        450: "Aram", 
        400: "Normals", 
        490: "swiftplay", 
        700: "Clash",
        720: "Aram Clash", 
        0: "Customs"
    }
    
    matchid = matchdata["metadata"]["matchId"]
    queuetype = queuetypebyid[matchdata["info"]["queueId"]]

    participantindex = get_participant_index(matchdata, request.cookies.get("puuid"))
    participantdata = matchdata["info"]["participants"][participantindex]
    for participant in matchdata["info"]["participants"]:
        if participant["puuid"] == request.cookies.get("puuid"):
            champused = participant["championName"]
        
    kills, deaths, assists = participantdata["kills"], participantdata["deaths"], participantdata["assists"]
    kda = round((kills+assists) / deaths, 2)

    if participantdata["teamPosition"] == "JUNGLE":
        csAt10 = participantdata["challenges"]["jungleCsBefore10Minutes"]
    else:
        csAt10 = participantdata["challenges"]["laneMinionsFirst10Minutes"]
    totalcs = participantdata["totalAllyJungleMinionsKilled"] + participantdata["totalEnemyJungleMinionsKilled"] + participantdata["totalMinionsKilled"]

    gamedurationminutes = (matchdata["info"]["gameDuration"]//60)
    gamedurationseconds = (matchdata["info"]["gameDuration"]%60)
    csPerMinute = totalcs / gamedurationminutes

    goldperminute = participantdata["challenges"]["goldPerMinute"]
    goldearned = participantdata["goldEarned"]
    winloss = participantdata["win"]

    return {
        "matchid": matchid,
        "queuetype": queuetype,
        "kda": kda,
        "kills": kills,
        "assists": assists,
        "deaths": deaths,
        "csAt10": csAt10,
        "csPerMinute": round(csPerMinute, 1),
        "goldperminute": goldperminute,
        "goldearned": goldearned,
        "gamedurationminutes": gamedurationminutes,
        "gamedurationseconds": gamedurationseconds,
        "winloss": winloss,
        "champused": champused
    }

def get_last20gamesstuff() -> list:
    """_summary_

    Returns:
        list: returns list of stats for 20 games
    """
    last20matchstats = []
    for matchid in (lolapi_matches(request.cookies.get("puuid", None))):  
        last20matchstats.append(get_stats(get_matchdata(matchid)))

    return last20matchstats

def get_avg20(matchid: str) -> dict:
    """_summary_

    Args:
        matchid (str): string of match id corresponding to the match

    Returns:
        dict: returns the stats of the player
    """
    kda, kills, deaths, assists, csAt10, csPerMinute, goldperminute = 0.00, 0, 0, 0, 0, 0, 0
    stats = get_stats(get_matchdata(matchid))
    # player kda for the most recent 20 matches
    for matchid in (lolapi_matches(request.cookies.get("puuid"))):
        kda += stats["kda"]
        kills += stats["kills"]
        assists += stats["assists"]
        deaths += stats["deaths"]
        csAt10 += stats["csAt10"]
        csPerMinute += stats["csPerMinute"]
        goldperminute += stats["goldperminute"]
    
    return {
        "last20kda": kda/20,
        "last20kills": kills/20,
        "last20assists": assists/20,
        "last20deaths": deaths/20,
        "last20csAt10": csAt10/20,
        "last20csPerMinute": csPerMinute/20,
        "last20goldperminute": goldperminute/20
    }

def get_playerstatsAt10(matchid: str, puuid: str) -> dict:
    """_summary_

    Args:
        matchid (str): id for the match you want stats from
        puuid (str): id of player that you want stats of

    Returns:
        dict: stats in dict format
    """
    api_url_timeline = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}/timeline?api_key={APIKEY_LOL}"
    resp = requests.get(api_url_timeline)
    matchdatatimeline = resp.json()

    participantid = get_participant_index(get_matchdata(matchid), puuid) + 1

    targettime = 600000  # 10 min in ms
    frames = matchdatatimeline["info"]["frames"]
    frameAt10 = min(frames, key=lambda f: abs(f["timestamp"] - targettime))

    pf = frameAt10["participantFrames"][str(participantid + 1)]
    cs = pf.get("minionsKilled", 0) + pf.get("jungleMinionsKilled", 0)

    # 4) Events up to 10:00 for K/D/A
    kills = deaths = assists = 0
    for f in frames:
        if f["timestamp"] > targettime:
            break
        for e in f.get("events", []):
            if e.get("type") != "CHAMPION_KILL":
                continue
            if e["timestamp"] > targettime:
                continue

            # killer
            if e.get("killerId") == participantid:
                kills += 1

            # victim
            if e.get("victimId") == participantid:
                deaths += 1

            # assists
            for aid in e.get("assistingParticipantIds", []) or []:
                if aid == participantid:
                    assists += 1
                    break

    kda = (kills + assists) / max(1, deaths)

    return {
        "gold": pf.get("totalGold"),
        "xp": pf.get("xp"),
        "cs": cs,
        "level": pf.get("level"),
        "kills_by10": kills,
        "deaths_by10": deaths,
        "assists_by10": assists,
        "kda_by10": round(kda, 2),
    }

def get_leaderboard(sortKey: str, reverse: bool) -> list:
    """_summary_

    Args:
        sortKey (str): Key to sort the players (e.g. kda)
        reverse (bool): order of sorting

    Returns:
        list: list of dictionaries containing player data
    """
    with open("./playerData/playerData.json", "r") as file:
        playerData = json.load(file)
    
    sortedPlayers = sorted(playerData, key=lambda p: p.get(sortKey, "kda"), reverse=reverse)

    return sortedPlayers

def get_playerData(puuid: str) -> dict:
    """_summary_

    Args:
        puuid (str): player's id for sheet query

    Returns:
        dict: contains stats about player
    """
    # json load (placeholder fo AWS DynamoDB API requests)
    with open("./playerData/playerData.json", "r") as file:
        playerData = json.load(file)
        # player data already exists in sheet
        if puuid in playerData:
            return playerData[puuid]
        
        # player data needs to be initialized in sheet
        return {
        "KDA_": {
            "kills": 0,
            "assists": 0,
            "deaths": 0,
        },
        "total_": {
            "totalDamageDealtToChampions": 0,
            "turretKills": 0,
            "goldEarned": 0,
            "objectivesStolen": 0,
        },
        "firstBloodKill": 0,
        "objectives": 0,
        "traits_": {
            "aggression": "",
            "weakness": "",
            "strength": "",
        },
        "reviewed_matchids": []
    }

def get_stats_to_save(matchid: int, puuid: str) -> dict:
    """_summary_

    Args:
        matchid (int): match id of corresponding game
        puuid (str): id of the player you wants stats of

    Returns:
        dict: stats that need to be saved to player sheet
    """
    match_data = get_matchdata(puuid)
    participantindex = get_participant_index(match_data, request.cookies.get("puuid"))
    participantdata = match_data["info"]["participants"][participantindex]
    return {
        "KDA_": {
            "kills": participantdata["kills"],
            "assists": participantdata["assists"],
            "deaths": participantdata["deaths"],
        },
        "total_": {
            "totalDamageDealtToChampions": participantdata["totalDamageDealtToChampions"],
            "turretKills": participantdata["turretKills"],
            "goldEarned": participantdata["goldEarned"],
            "objectivesStolen": participantdata["objectivesStolen"],
        },
        "firstBloodKill": participantdata["firstBloodKill"],
        "objectives": participantdata["objectives"],
    }