import discord
import json
from discord.ext import commands
from datetime import datetime
from copy import deepcopy
import os
import gspread

scoreboard = "Scoreboard.json"

# Load token from BotTokens.txt
tokenPath = 'C:/Users/pphue/Documents/Coding/DiscordBot/bottokens.txt'
with open(tokenPath, 'r') as f:
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

# token = os.environ.get('botToken')

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

    if 'TESTBOT TESTBOT TESTOBOT' in message.content:
        await message.channel.send('TimeGuessr #1033 — 15,000/50,000')

    # Check for TimeGuessr message
    isTimeGuessrMessage = 'TimeGuessr #' in message.content and '/50,000' in message.content.lower() #and message.author != bot.user
    if isTimeGuessrMessage:
        print('timeguessr message detected')

        gc = gspread.service_account(filename='C:/Users/pphue/Documents/Coding/DiscordBot/timeguessrdiscordbot-7ca8cf233bad.json')
        sh = gc.open("Discord TimeGuessr Scoreboard")
        scoreboard = sh.sheet1

        player, puzzleNumber, score = parseTimeGuessrMessage(message)
        playerCol, gameRow = updateScoreboard(player, puzzleNumber, score, scoreboard)
        scoreboardInfo = retrieveFromScoreboard(puzzleNumber, scoreboard, playerCol, gameRow)
        print('scoreboardInfo:')
        print(scoreboardInfo)
        outMessage = buildMessage(scoreboardInfo, puzzleNumber)

        await message.channel.send(outMessage)

def parseTimeGuessrMessage(message):
    # Example message: "TimeGuessr #1030 34,235/50,000"
    # Example message: "TimeGuessr #1030 - 34,235/50,000"
    try:
        player = message.author.name
        parts = message.content.split()
        gameNum = 0
        score = 0
        for p in parts:
            if '#' in p:
                gameNum = int(p[1:])
            elif '/' in p:
                score = p.split('/')[0].replace(',', '')

        print('parts:  ', parts, ' ', gameNum, ' ', score)
        return player, gameNum, score
    except Exception as e:
        print(f'Error parsing TimeGuessr message: {e}')
    return None, None

def updateScoreboard(player, puzzleNumber, score, scoreboard):
    print('Updating scoreboard for ', player)

    # If new player, add to PlayerList
    playerList = scoreboard.get('E1:Z1')
    print(playerList)
    if player not in playerList[0]:
        print('player not here yet  ', player)
        topRow = scoreboard.row_values(1)
        newestPlayer = topRow[-1]
        print('newestplayer: ', newestPlayer)
        newestPlayerCol = scoreboard.find(newestPlayer).col
        print('newestPlayerCol: ', newestPlayerCol)
        playerTemplate = scoreboard.get('E2:E4')
        playerCol = newestPlayerCol+1
        scoreboard.update_cell(1, playerCol, player)
        for row in range(2,5):
            scoreboard.update_cell(row, playerCol, playerTemplate[row-2][0])
    else:
        playerCol = scoreboard.find(player).col

    # Create new game if first of the day
    gameString = "Game" + str(puzzleNumber)
    gamesCol = scoreboard.col_values(1)
    if gameString not in gamesCol:
        print(gameString, ' not found in   ', gamesCol)
        gameRow = createDailyGame(gameString, gamesCol, scoreboard)
        # Populate correct info
        populateTodaysGame(gameRow, scoreboard)
    else:
        gameRow = scoreboard.find(gameString).row
    print('gamesow: ', gameRow)

    # Add player to Daily Game
    playerScoreToday = scoreboard.cell(gameRow, playerCol).value
    if playerScoreToday == 0 or playerScoreToday == None:
        scoreboard.update_cell(gameRow, playerCol, int(score))
    # If player has score for today - do nothing

    # Update player's info
    gamesPlayed = scoreboard.cell(2,playerCol).value
    runningTot = scoreboard.cell(3,playerCol).value
    print('runningTot: ', runningTot)
    print(' new runningTot: ', int(runningTot[0])+int(score))
    avgScore = round((int(runningTot)+int(score))/(int(gamesPlayed)+1))
    print('gameplayed, running tot, avg', gamesPlayed, '  ', runningTot, '   ', avgScore)
    scoreboard.update_cell(2,playerCol, int(gamesPlayed)+1)
    scoreboard.update_cell(3,playerCol, int(runningTot)+int(score))
    scoreboard.update_cell(4,playerCol, avgScore)

    return playerCol, gameRow

def populateTodaysGame(gameRow, scoreboard):
    todaysDate = datetime.today().strftime('%Y-%m-%d').split('-')
    scoreboard.update_cell(gameRow, 2, int(todaysDate[0]))
    scoreboard.update_cell(gameRow, 3, int(todaysDate[1]))
    scoreboard.update_cell(gameRow, 4, int(todaysDate[2]))

def createDailyGame(gameString, gamesCol, scoreboard):
    # Add new game to scoreboard
    lastGame = gamesCol[-1]
    # print('last game ', lastGame)
    gameRow = scoreboard.find(lastGame).row 
    scoreboard.update_cell(gameRow+1, 1, gameString)
    # print('updated row ', gameRow+1, ' with teh latest game')
    return gameRow+1

def retrieveFromScoreboard(puzzleNumber, scoreboard, playerCol, gameRow):
    print('Retrieving scoreboard')
    playerList = scoreboard.get('E1:Z1')

    infoRanked = []

    # [playerName, score]
    # print('playerlist: ' , playerList)
    # print(len(playerList[0]))
    for col in range(1,len(playerList[0])+1):
        readCol = col+4
        # print('col  ', col, '   ', readCol)
        playerLine = []
        pName = scoreboard.cell(1,readCol).value
        pScore = scoreboard.cell(gameRow,readCol).value
        playerLine.append(pName)
        playerLine.append(pScore)
        # print(playerLine)
        if pScore != None and int(pScore) > 0:
            infoRanked = insertPlayerByRank(playerLine, infoRanked) 

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