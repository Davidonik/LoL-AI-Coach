import json
import boto3
import requests

lol_api = "RGAPI-dcf2e12a-26c7-41c3-abbb-ecd4add5b06b"

playerData_path = "./playerData"

# LoL API Get Data
def getData():
    # Player Info
    summonername = "KiraKuin"
    tagline = "Lover"
    api_url_player = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summonername}/{tagline}&api_key={lol_api}"
    resp = requests.get(api_url_player)
    playerinfo = resp.json()

    # 20 most recent match info
    playerPUUID = playerinfo["puuid"]
    api_url_matches = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{playerPUUID}/ids?start=0&count=20&api_key={lol_api}"
    resp = requests.get(api_url_matches)
    matchdata = resp.json()
    

    

# Parse LoL API Data
def dataParse():
    raise NotImplemented

game_data = ""

# Bedrock Model Configs
bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
model_id = "arn:aws:bedrock:us-east-1:085366697379:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"

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
    "You are reviewing a player's recent ranked game. The following data is provided:\n"
    # "{player_info}"
    # "{champion_data}"
    # "{game_data}"
    # "The player is playing Miss Fortune against Xayah in the ADC Role. "
    # "At 10 minutes, Miss Fortune has 4295 gold and Xayah has 3458 gold. "
    # "Miss Fortune has 75 cs and Xayah has 57 cs. "
    "Miss Fortune has a 5.0 KDA and Xayah has a 0.75 KDA. "
    "Focus on laning phase performance — last-hitting, positioning, early wave control trading with opponents.\n"
)

task = (
    "Identify the lane result, whether the player ended up behind, even, or ahead of the opposing laner at the 10 minute mark based on the player's gold, level, and KDA. "
    "Next identify the top 2-3 mistakes in the laning phase and explain how they affected the player's result at the 10 minute mark. "
    "Then provide 2 actionable coaching tips with clear timings or cues (e.g., 'At 3:15 when wave 3 crashes…'). "
    "Provide a summary of the player's tendencies for lane aggression and play style. "
)

prompt = f"{base} {context} {task}"
print(prompt)

# AWS Request Structure
body = {
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 1000,
    "anthropic_version": "bedrock-2023-05-31",
}

# Send the request to AWS Bedrock
response = bedrock.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json",
    accept="application/json"
)

# The response body comes as a byte stream, so decode it:
response_body = json.loads(response["body"].read())

# Print the result
print("\n Model output:")
print(response_body["content"][0]["text"])
