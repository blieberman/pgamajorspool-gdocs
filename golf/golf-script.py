#!/usr/bin/env python

import json
import requests
import time
import datetime
import os
import logging
import gspread
import sys
from collections import defaultdict
import operator
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
                round_score = player["today"]
                thru = player["thru"]
                if not thru:
                    round_score = ""
                mainsh.update_cell(gplayer.row, (gplayer.col + ROUND), round_score)
                # debug
                print("%s: %s" % (name, round_score))
                break

    # create ranked scoreboard for google sheet entries
    # create an entry to scores dict
    entry_score = defaultdict(int)

    entries_clist = mainsh.range('B1:Q1')
    for entry in entries_clist:
        ename = entry.value
        if ename:
            weighted_score = int(mainsh.cell((entry.row + 7), entry.col).value)
            entry_score[ename] = weighted_score

    entries_clist = mainsh.range('B10:Q10')
    for entry in entries_clist:
        ename = entry.value
        if ename:
            weighted_score = int(mainsh.cell((entry.row + 7), entry.col).value)
            entry_score[ename] = weighted_score

    # sort the dict by weighted score
    ordered_entry_score = sorted(entry_score.items(), key=operator.itemgetter(1))
    range_build = "T" + str(3) + ":U" + str(27)
    cell_list = mainsh.range(range_build)

    cell_index = 0

    for entry in ordered_entry_score:
        entry_name = entry[0]
        score = entry[1]

        if entry_name and score:
            cell_list[cell_index].value = str(entry_name)
            cell_index += 1
            cell_list[cell_index].value = str(score)
            cell_index += 1
            logging.info("Adding (%s, %s)" % (entry_name, score))

    mainsh.update_cells(cell_list)


if __name__ == '__main__':
    sys.exit(main())
