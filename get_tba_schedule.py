#!/usr/bin/env python3

import json
import argparse
import itertools
import urllib, urllib.request, urllib.error
from urllib.request import Request

# Set up cli arguments
parser = argparse.ArgumentParser(description='Return a csv match schedule for a given event key')
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
parser.add_argument('--bluefirst',
                    '-b',
                    dest='blue_first',
                    action='store_true',
                    required=False,
                    help='Format csv with blue alliance first')
parser.add_argument('--keepprefix',
                    '-p',
                    dest='keep_prefix',
                    action='store_true',
                    required=False,
                    help='Keep the "frc" prefix on team numbers')
parser.add_argument('--hidenumbers',
                    '-n',
                    dest='hide_numbers',
                    action='store_true',
                    required=False,
                    help='Don\'t print match numbers before team numbers.')

args = parser.parse_args()

# Get match information.  Headers are needed to authenticate with TBA.
request = Request(
    url=f'https://thebluealliance.com/api/v3/event/{args.event_key}/matches',
    headers={
            'X-TBA-Auth-Key': args.tba_key,
            'User-Agent': 'Schedule script'
                        })
try:
    response = urllib.request.urlopen(request)
except urllib.error.HTTPError as e:
    # Handle error responses & provide context on the problem
    print(f'{e.code} {e.reason}\n{e.read().decode("utf-8")}')
    exit(e.code)



match_information = json.loads(response.read().decode('utf-8'))
match_information.sort(key=lambda x: x['match_number'])  # sort by match number
schedule = itertools.filterfalse(lambda x: x['comp_level'] != 'qm', match_information)
# drop all elimination matches.  This yields a generator, not a list, so it has to be the last operation.

for match in schedule:
    teams = []

    for team in match['alliances']['red']['team_keys']:
        if not args.keep_prefix:
            team = team.lstrip('frc')
        teams.append(team)

    team_size = len(teams)
    for team in match['alliances']['blue']['team_keys']:
        if not args.keep_prefix:
            team = team.lstrip('frc')
        if args.blue_first:
            teams.insert(len(teams) - team_size, team)
        else:
            teams.append(team)

    if not args.hide_numbers:
        teams.insert(0, str(match['match_number']))

    print(','.join(teams))
