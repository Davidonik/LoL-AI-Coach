import json
import boto3
import requests
import os
from flask import Flask, request, jsonify, make_response, redirect, url_for, render_template
from flask_cors import CORS

# API Key for LoL
APIKEY_LOL = "RGAPI-a24b298f-5f2e-4c8c-890c-5bc8cc010a2b"

#######################################################
###################### FLASH APP ######################
#######################################################

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500", "http://localhost:5500"]
)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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

@app.route("/aws/ai_coach", methods=["POST"])
def ai_coach():
    # Bedrock Model Configs
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    model_id = "arn:aws:bedrock:us-east-1:085366697379:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"

    player_info = get_playerData(request.cookies.get("puuid"))
    champion_data = get_champdata()
    game_data = lolapi_matches(request.cookies.get("puuid"))

    # AI Prompt Creation
    base = (
        "You are a Challenger-ranked League of Legends coach with over 10 years of competitive and analytical experience. " 
        "Your tone is confident, encouraging, and professional — like a high-ELO coach reviewing a player's match history. " 
        "You focus on actionable, measurable advice with in-game reasoning (timing, wave control, map awareness, etc.). " 
        "Use game-specific vocabulary correctly (e.g., roam timings, CS@10, lane priority, objective control, tempo, macro). " 
        "Avoid fluff or generic comments. Always explain why each issue matters in terms of win conditions and map state." 
        "When data is unclear, infer gently — never guess random numbers. " 
        "Keep answers concise and structured. "
    )

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
        # "Given this player's tendencies:\n"
        # f"{str(playerData["traits_"].keys())} give a one word label for each trait in the format of a json file. "
    )

    prompt = f"{base} {context} {task}"
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
    aws_response = bedrock.invoke_model(
        modelId=model_id,
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
    
    matchdata = resp.json()
    return matchdata

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

def get_kda():
    raise NotImplemented

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
                "total": None,
                "last20": None,
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