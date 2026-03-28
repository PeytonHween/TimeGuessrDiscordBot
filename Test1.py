import discord
import json
from discord.ext import commands
from datetime import datetime
from copy import deepcopy

scoreboard = "Scoreboard.json"

# Load token from BotTokens.txt
with open('BotTokens.txt', 'r') as f:
    content = f.read()
    # Extract token between < and >
    start = content.find('<')
    end = content.find('>')
    if start != -1 and end != -1:
        token = content[start+1:end]
    else:
        # Fallback: get second line if no < > markers
        lines = content.strip().split('\n')
        token = lines[1] if len(lines) > 1 else None

#############################

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('----------------')

@bot.command()
async def hello(ctx): # bot looks for !hello
    await ctx.send('Hello!') # response

@bot.command()
async def poop(ctx):
    await ctx.send('peepee lol')
'''
Goals
'''

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')

    # Check for TimeGuessr message
    isTimeGuessrMessage = 'TimeGuessr' in message.content and '/50,000' in message.content.lower() and message.author != bot.user
    if isTimeGuessrMessage:

        player, puzzleNumber, score = parseTimeGuessrMessage(message)
        newBoard = updateScoreboard(player, puzzleNumber, score, scoreboard)
        print(newBoard)
        writeToScoreboard(scoreboard, newBoard)
        scoreboardInfo = retrieveFromScoreboard(newBoard, puzzleNumber)
        print('scoreboardInfo:')
        print(scoreboardInfo)
        outMessage = buildMessage(scoreboardInfo, puzzleNumber)

        await message.channel.send(outMessage)

def writeToScoreboard(scoreboard, newBoard):
    print('Writing to scoreboard')
    json_str = json.dumps(newBoard, indent=4)
    with open(scoreboard, "w") as f:
        f.write(json_str)

def parseTimeGuessrMessage(message):
    # Example message: "TimeGuessr #1030 34,235/50,000"
    try:
        player = message.author.name
        parts = message.content.split()
        num = parts[1][1:]
        scoreParts = parts[2].split('/')[0].replace(',', '')
        return player, num, scoreParts
    except Exception as e:
        print(f'Error parsing TimeGuessr message: {e}')
    return None, None

def updateScoreboard(player, puzzleNumber, score, file):
    print('Updating scoreboard for ', player)

    with open(file, "r") as f:
        scoreboard = json.load(f)

    # If new player, add to PlayerList
    playerList = scoreboard['PlayerList']
    if player not in playerList:
        playerTemplate = playerList['Test Player']
        playerList[player] = deepcopy(playerTemplate)
        playerList[player]['ID'] = scoreboard['PlayerList']['MaxPlayerID'] + 1
        scoreboard['PlayerList']['MaxPlayerID'] += 1
    
    # Crate new game if first of the day
    gameString = "Game" + str(puzzleNumber)
    if gameString not in scoreboard['DailyGames']:
        createDailyGame(gameString, scoreboard['DailyGames'])
        # Populate correct info
        todaysGame = scoreboard['DailyGames'][gameString]
        populateTodaysGame(todaysGame)

    # Add player to Daily Game
    dailyScores = scoreboard['DailyGames'][gameString]['DailyScores']
    if player not in dailyScores:
        dailyScores[player] = int(score)
    # If player has score for today - do nothing

    # Update player's info
    playerList[player]['Running Total'] +=  int(score)
    playerList[player]['Games Played'] += 1
    playerList[player]['Average Score'] = round( playerList[player]['Running Total'] / playerList[player]['Games Played'])

    return scoreboard

def populateTodaysGame(todaysGame):
    todaysDate = datetime.today().strftime('%Y-%m-%d').split('-')

    todaysGame['Year'] = int(todaysDate[0])
    todaysGame['Month'] = int(todaysDate[1])
    todaysGame['Day'] = int(todaysDate[2])

def createDailyGame(gameString, dailyGames):
    # Add new game to scoreboard
    gameTemplate = dailyGames['Game0']
    dailyGames[gameString] = deepcopy(gameTemplate)

def retrieveFromScoreboard(newBoard, puzzleNumber):
    print('Retrieving scoreboard')
    gameString = "Game" + str(puzzleNumber)
    playerList = newBoard['PlayerList']
    dailyGame = newBoard['DailyGames'][gameString]
    dailyScores = dailyGame['DailyScores']

    infoRanked = []

    for playerName in dailyScores:
        playerLine = []
        playerLine.append(playerName)
        playerLine.append(dailyScores[playerName])
        infoRanked = insertPlayerByRank(playerLine, infoRanked) 
        # print('infoRanked')
        # print(infoRanked)

    return infoRanked

def insertPlayerByRank(playerLine, infoRanked):
    if len(infoRanked) < 1:
        return [playerLine]
    
    score = playerLine[1]
    for idx, p in enumerate(infoRanked):
        if score > p[1]:
            infoRanked.insert(idx, playerLine)
            return infoRanked
        elif idx == len(infoRanked)-1:
            infoRanked.append(playerLine)
            return infoRanked


def buildMessage(scoreboardInfo, puzzleNumber):
    print('Displaying message')
    # print(scoreboardInfo)
    newMessage = 'TimeGusser #' + str(puzzleNumber) + ' Leaderboard :earth_americas:' + ':date:' + '\n '
    pos = 1
    for line in scoreboardInfo:
        player = line[0]
        dailyScore = line[1]
        rankText = getRankText(pos)
        newMessage += rankText
        newMessage += ': '
        newMessage += player
        newMessage += ": "
        newMessage += str(dailyScore)
        newMessage += '\n '
        pos += 1
    return newMessage

def getRankText(pos):
    match pos:
        case 1:
            return ':first_place:'
        case 2:
            return ':second_place:'
        case 3:
            return ':third_place:'
        case 4:
            return ':four:'
        case 5:
            return ':five:'
        case 6:
            return ':six:'
        case 7:
            return ':seven:'
        case 8:
            return ':eight:'
        case 9:
            return ':nine:'
        case 10:
            return ':keycap_ten:'
        case _:
            return str(pos)

bot.run(token)