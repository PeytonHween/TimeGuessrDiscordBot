import gspread

gc = gspread.service_account(filename='C:/Users/pphue/Documents/Coding/DiscordBot/timeguessrdiscordbot-7ca8cf233bad.json')

sh = gc.open("Discord TimeGuessr Scoreboard")
scoreboard = sh.sheet1
print(scoreboard.get('A1:Z1'))
print(scoreboard.cell(1,2).value)
playerList = scoreboard.get('E1:Z1')
print(['Test Player'] in playerList)
print(scoreboard.get('E2:E4'))
cell = scoreboard.find("Test Player")
print(cell.row)

player = 'phuene'
testPlayer = scoreboard.find("Test Player")
playerTemplate = scoreboard.get('E2:E4')
scoreboard.update_cell(testPlayer.row, testPlayer.col+1, player)
for row in range(2,5):
    scoreboard.update_cell(row, testPlayer.col+1, playerTemplate[row-2][0])