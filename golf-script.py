#!/usr/bin/python

import gspread
import json
import requests
import time
import datetime

def getRound():
  round = datetime.datetime.today().weekday() - 2
  return round

from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()
credentials = credentials.create_scoped(['https://spreadsheets.google.com/feeds'])

GOLF_LEADERBOARD = "http://api.sportsdatallc.org/golf-t1/leaderboard/pga/2015/tournaments/f5897f1c-159d-432f-b774-50438ee6e0c7/leaderboard.json?api_key=47cck4gyk9zsa4crkjthtkcn"
ROUND = getRound()

gc = gspread.authorize(credentials)
sh = gc.open_by_key('1bDt2NQulTVks0UFypCtD80YC9yR5HkjxHwCW3m2lmNs')

mainsh = sh.worksheet("Open Championship 2015")
players_clist = mainsh.range('A13:A37')

r = requests.get(GOLF_LEADERBOARD)
scores = r.json()

for player in scores["leaderboard"]:
  name = player["first_name"] + " " + player["last_name"]

  for gplayer in players_clist:
    gname = gplayer.value
    if (name == gname and not player.has_key("status")):
      score = player["rounds"][ROUND - 1]["score"]
      mainsh.update_cell(gplayer.row, (gplayer.col + ROUND), score)
      print score
      break

  time.sleep(1)
