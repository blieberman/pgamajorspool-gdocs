#!/usr/bin/python

import gspread
import json
import requests
import time
import datetime
from oauth2client.client import GoogleCredentials

SPORTSAPI_KEY = ""
SPORTSAPI_TOURAMENT = ""
GOLF_LEADERBOARD = "http://api.sportsdatallc.org/golf-t1/leaderboard/pga/2015/tournaments/" + SPORTSAPI_TOURAMENT + "/leaderboard.json?api_key=" + SPORTSAPI_KEY
GDOC_KEY = ""
GDOC_SHEET_NAME = ""

# returns round number based on day of week
def getRound():
  round = datetime.datetime.today().weekday() - 2
  return round

###AUTHENTICATION TO GOOGLE###
credentials = GoogleCredentials.get_application_default()
credentials = credentials.create_scoped(['https://spreadsheets.google.com/feeds'])

gc = gspread.authorize(credentials)
sh = gc.open_by_key(GDOC_KEY)
######

ROUND = getRound()

###OPEN SPREADSHEET###
mainsh = sh.worksheet(GDOC_SHEET_NAME)
# set player name range based on your spreadsheet
players_clist = mainsh.range('A13:A37')

# get the full leaderboard
r = requests.get(GOLF_LEADERBOARD)
scores = r.json()

# parse scores and push data to spreadsheet in correct format
for player in scores["leaderboard"]:
  name = player["first_name"] + " " + player["last_name"]

  for gplayer in players_clist:
    gname = gplayer.value
    if (name == gname and not player.has_key("status")):
      score = player["rounds"][ROUND - 1]["score"]
      mainsh.update_cell(gplayer.row, (gplayer.col + ROUND), score)
      print score
      break
# 1 call/sec limit on trial sports api
  time.sleep(1)
