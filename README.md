# **LoL-AI-Coach**
A League of Legends AI Coach is like a personal digital trainer that watches how you play and gives you feedback — just like a real coach would.

It uses game data from your matches (like what champion you played, how many times you died, etc.) and compares it to what skilled players usually do.

Then it gives you tips, analysis, and goals to help you improve faster.

## How It Works
### 1. Connects to your game data
It uses Riot Games’ official API to read information about your recent matches — such as your stats, what happened in the game, and what champion you played.

### 2. Understands your champion
The AI knows what each champion is supposed to do — for example:

*Ashe is a ranged marksman who deals steady damage from afar.*

**OR**

*Leona is a tank who protects her teammates and starts fights.*

So it won’t compare Ashe and Leona the same way; it gives advice that fits your champion’s role and playstyle.

### 3. Analyzes your performance
It looks at things like:
- How often you die vs. how much damage you deal
- Whether you buy the right items for your champion
- How much gold or experience you earn compared to others
- If you ward enough or help with objectives

### 4. Gives personalized feedback
Instead of vague tips, it might say things like:

“You played Ahri this game. Your early-game farm was strong, but you roamed later than usual for a mid-laner. Try pushing the wave faster before leaving lane.”

**OR**

“You built too many damage items as Leona — next time, prioritize armor and magic resistance to stay alive longer.”  #change this line

### 5.Tracks your improvement over time
The AI can also store your match history and highlight progress — like “You’ve improved your farming speed by 15% in the last 10 games.”

## Setup
1. Download [Python 3.13.7 64-bit](https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe) or [Python 3.13.7 32-bit](https://www.python.org/ftp/python/3.13.7/python-3.13.7.exe)
2. Open a terminal, select powershell and run   `python -m venv venv` in VS code 
3. Activate the venv using  `.\venv\Scripts\activate`
4. Run  `pip install -r requirements.txt`, after that run   `pip install awscli` and    `aws configure`
5. Add your credentials
