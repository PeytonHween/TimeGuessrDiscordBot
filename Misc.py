import json

scoreboard = "Scoreboard.json"

with open(scoreboard, "r") as f:
    data = json.load(f)

print(data)