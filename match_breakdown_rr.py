#!/usr/bin/env python3

import argparse
import json
from enum import Enum

import urllib, urllib.request, urllib.error
from urllib.request import Request

# define data class
class Team_Data:
    class TaxiValues(Enum):
        TRUE = 'Taxi'
        FALSE = 'Did not move'

    def __init__(self):
        self.matchNumber = 0
        self.teamNumber = 0
        self.taxi = self.TaxiValues.FALSE
        self.climb = 'None'
        self.autoCargo = 0
        self.teleopCargo = 0
        self.quintet = False
        self.fouls = 0
        self.techFouls = 0
        self.rankingPoints = 0
        self.foulPoints = 0
        self.score = 0

    def __str__(self) -> str:
        return '{},{},{},{},{},{},{},{},{},{},{},{}'\
        .format(
            self.matchNumber,
            self.teamNumber,
            self.taxi,
            self.climb,
            self.autoCargo,
            self.teleopCargo,
            self.quintet,
            self.fouls,
            self.techFouls,
            self.rankingPoints,
            self.foulPoints,
            self.score
        )

# Set up cli arguments
parser = argparse.ArgumentParser(description='Return a csv match breakdown for a given event')
parser.add_argument('--event',
                    '-e',
                    dest='event_key',
                    action='store',
                    required=True,
                    metavar='event_key',
                    help='TBA Event Key to use')
parser.add_argument('--apikey',
                    '-k',
                    dest='tba_key',
                    action='store',
                    required=True,
                    metavar='tba_api_key',
                    help='TBA Read API key to use when making the request')


args = parser.parse_args()

# I know I can get this with the "year" key in the event/EVENTKEY endpoint
# but it seems like a waste when you can usually get it from the event key itself
# if someone hosts a RR event in 2023+ they can open an issue :)
if not args.event_key.startswith("2022"):
    print('This script is only for 2022 Rapid React events!')
    exit(1)

request = Request(
    url=f'https://thebluealliance.com/api/v3/event/{args.event_key}/matches',
    headers={
                'X-TBA-Auth-Key': args.tba_key,
                'User-Agent': 'Schedule script'
            }
)
# Get match information.  Headers are needed to authenticate with TBA.
try:
    response = urllib.request.urlopen(request)
except urllib.error.HTTPError as e:
    # Handle error responses & provide context on the problem
    print(f'{e.code} {e.reason}\n{e.read().decode("utf-8")}')
    exit(e.code)

data = json.loads(response.read().decode('utf-8'))
# Auto taxi points, Auto cargo total, Teleop total cargo, quintet achieved, foul count, tech-foul count, ranking points, foul points, Score
TABLE_HEADING = 'Matches,{},AUT_TAXI,TOP_CL,CV_ATP,CV_ACT,CV_TCT,CV_QT,CV_FOUL,CV_TFOUL,CV_RP,CV_FP,CV_SCORE'
output_data = {
    'RED1': [TABLE_HEADING.format('Red 1')],
    'RED2': [TABLE_HEADING.format('Red 2')],
    'RED3': [TABLE_HEADING.format('Red 3')],
    'BLUE1': [TABLE_HEADING.format('Blue 1')],
    'BLUE2': [TABLE_HEADING.format('Blue 2')],
    'BLUE3': [TABLE_HEADING.format('Blue 3')],
}

for match in data:
    team_data = Team_Data()

    team_data.matchNumber = match['match_number']
    for alliance in match['alliances']:
        alliance_breakdown = match['score_breakdown'][alliance]
        team_data.score = match['alliances'][alliance]['score']

        team_data.autoCargo = alliance_breakdown['autoCargoTotal']
        team_data.teleopCargo = alliance_breakdown['teleopCargoTotal']
        team_data.quintet = alliance_breakdown['quintetAchieved']
        team_data.fouls = alliance_breakdown['foulCount']
        team_data.techFouls = alliance_breakdown['techFoulCount']
        team_data.rankingPoints = alliance_breakdown['rp']
        team_data.foulPoints = alliance_breakdown['foulPoints']
        
        teams = match['alliances'][alliance]['team_keys']
        for i in range(1, len(teams)+1):
            if alliance_breakdown[f'taxiRobot{i}'] == 'Yes':
                team_data.taxi = Team_Data.TaxiValues.TRUE
            else:
                team_data.taxi = Team_Data.TaxiValues.FALSE
            
            team_data.climb = alliance_breakdown[f'endgameRobot{i}']
            team_data.teamNumber = teams[i].lstrip('frc')

            output_data[f'{alliance.upper()}{i}'].append(str(team_data))

for table in output_data.keys():
    for row in output_data[table]:
        print(row)
