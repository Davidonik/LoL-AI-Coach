import json
import boto3
import requests
import os
from flask import Flask, request, jsonify, make_response, redirect, url_for, render_template
from flask_cors import CORS

# API Key for LoL
APIKEY_LOL = "RGAPI-a24b298f-5f2e-4c8c-890c-5bc8cc010a2b"

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

CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500", "http://localhost:5500"]
)

@app.route("/")
def home():
    return render_template("leaderboard.html")

@app.route("/dashboard")
def dashboard():
    ign = f"{request.cookies.get("sname", "")}#{request.cookies.get("tag", "")}"
    return render_template("dashboard.html", ign=ign)

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
    player_info = get_playerData(request.cookies.get("puuid"))
    champion_data = get_champdata()
    game_data = get_matchdata() #TODO fetch the matchid after button is made for it

    # AI Prompt Creation
    context = (
        f"""You are reviewing a player's recent ranked game. The following data is provided:\n
        # {player_info}
        # {champion_data}
        # {game_data}
        # The player is playing Miss Fortune against Xayah in the ADC Role. 
        # At 10 minutes, Miss Fortune has 4295 gold and Xayah has 3458 gold.
        # Miss Fortune has 75 cs and Xayah has 57 cs. "
        # Miss Fortune has a 5.0 KDA and Xayah has a 0.75 KDA.
        "Focus on laning phase performance — last-hitting, positioning, early wave control trading with opponents.\n
        """
    )

    task = (
        "Identify the lane result, whether the player ended up behind, even, or ahead of the opposing laner at the 10 minute mark based on the player's gold, level, and KDA. "
        "Next identify the top 2-3 mistakes in the laning phase and explain how they affected the player's result at the 10 minute mark. "
        "Then provide 2 actionable coaching tips with clear timings or cues (e.g., 'At 3:15 when wave 3 crashes…'). "
    )

    prompt = f"{BASE} {context} {task}"
    # print(prompt)

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

    # Create response object
    # print("\n Model output:")
    # print(aws_response_body["content"][0]["text"])
    response = make_response(jsonify({
        "message": True,
        "ai_response": aws_response_body["content"][0]["text"]
    }))
    
    return response

@app.route("/api/get_matches", methods=["POST"])
def getLast20Matches():
    puuid = request.cookies.get("puuid", None)
    if None == puuid:
        return make_response(jsonify({"error": f"summoner not found"}))
    return lolapi_matches(puuid)


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


def lolapi_matches(puuid: str) -> dict:
    """_summary_

    Args:
        puuid (str): player's PUUID

    Returns:
        dict: matchdata 
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

    playerindex = matchdata["metadata"]["participants"].indexOf(puuid)

    player = matchdata["info"]["participants"][playerindex]
    opponent = matchdata["info"]["participants"][(playerindex + 5) % 2]
    
    return {
        "player": player,
        "opponent": opponent,
    }

#############################################################
####################### GET FUNCTIONS #######################
#############################################################

def get_champdata(folderpath="champions") -> dict:
    """_summary_

    Args:
        folderpath (str, optional): path to champion data dir. Defaults to "champions".

    Returns:
        dict: data on champions
    """
    championdata = {}
    matchdata = lolapi_matches(request.cookies.get("puuid"))

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

def get_matchdata(matchid: str) -> dict:
    """_summary_

    Args:
        matchid (str): match id of the chosen match.

    Returns:
        dict: data on the match
    """
    api_url_match = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={APIKEY_LOL}"
    resp = requests.get(api_url_match)
    matchdata = resp.json()

    return matchdata

def get_participant_index(matchdata: dict, puuid: str) -> int | None:
    """_summary_

    Args:
        matchdata (dict): match data of the chosen match.
        puuid (str): player's id for query

    Returns:
        dict: Returns the participant index (0 to 9) for a given player's PUUID.
    """
    for i, p in enumerate(matchdata["info"]["participants"]):
        if p["puuid"] == puuid:
            return i
    return None


def get_kda(matchdata: dict) -> dict:
    """_summary_

    Args:
        matchdata (dict): match data of the chosen match.

    Returns:
        dict: returns the kda, kills, deaths, assists
    """
    participantindex = get_participant_index(matchdata, request.cookies.get("puuid"))
    participantdata = matchdata["info"]["participants"][participantindex]
    kills, deaths, assists = participantdata["kills"], participantdata["deaths"], participantdata["assists"]
    kda = round((kills+assists) / deaths, 2)

    return {
        "kda": kda,
        "kills": kills,
        "deaths": deaths,
        "assists": assists
    }

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
        last20kda = 0.00
        
        # player data already exists in sheet
        if puuid in playerData:
            return playerData[puuid]
        
        # player kda for the most recent 20 matches
        for matchid in (lolapi_matches(puuid)):
            last20kda += get_kda(get_matchdata(matchid))["kda"]
        
        # player data needs to be initialized in sheet
        return {
            "KDA_": {
                "kda": None,
                "last20": last20kda
            },
            "avg_": {
                "deaths": None,
                "cs@10": None,
                "cs_per_min": None,
                "gold_per_min": None,
            },
            "total_": {
                "dmg_done": None,
                "towers_taken": None,
                "gold": None,
                "objectives": None,
                "objective_steals": None,
                "first_bloods": None,
                "feats": None,
            },
            "traits_": {
                "aggression": None,
                "weakness": None,
                "strength": None,
            }
        }