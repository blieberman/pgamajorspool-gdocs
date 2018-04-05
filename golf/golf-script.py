#!/usr/bin/env python

import json
import requests
import time
import datetime
import os
import logging
import gspread
import sys
from oauth2client.service_account import ServiceAccountCredentials

# get the id at https://statdata.pgatour.com/r/current/message.json
TOURNAMENT_ID = "014"
GOLF_LEADERBOARD = "https://statdata.pgatour.com/r/" + TOURNAMENT_ID + "/leaderboard-v2mini.json"

GDOC_JSON_KEY_PATH = os.path.join(os.path.expanduser("~"), 'google_application_credentials.json')
GDOC_KEY = "1bDt2NQulTVks0UFypCtD80YC9yR5HkjxHwCW3m2lmNs"
GDOC_FEED_ENDPOINT = "https://spreadsheets.google.com/feeds"
GDOC_SHEET_NAME = "Masters 2018"


# returns round number based on day of week
def getRound():
    round = datetime.datetime.today().weekday() - 2
    return round


def main():
    # authenticate to google
    scope = [GDOC_FEED_ENDPOINT]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GDOC_JSON_KEY_PATH, scope)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(GDOC_KEY)
    # open spreadsheet
    mainsh = sh.worksheet(GDOC_SHEET_NAME)
    # set player name range based on your spreadsheet
    players_clist = mainsh.range('A24:A60')
    # get the round
    ROUND = getRound()
    # get the full leaderboard from api
    r = requests.get(GOLF_LEADERBOARD)
    scores = r.json()

    # parse scores and push data to spreadsheet in correct format
    for player in scores["leaderboard"]["players"]:
        name = player["player_bio"]["first_name"] + " " + player["player_bio"]["last_name"]

        for gplayer in players_clist:
            gname = gplayer.value
            if name == gname and player["status"] == "active":
                score = player["rounds"][ROUND - 1]["strokes"]
                today = player["today"]
                if not today:
                    score = ""
                mainsh.update_cell(gplayer.row, (gplayer.col + ROUND), score)
                # debug
                print("%s: %s" % (name, score))
                break


if __name__ == '__main__':
    sys.exit(main())
