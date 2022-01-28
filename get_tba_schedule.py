#!/usr/bin/env python3

import json
import argparse
import itertools

try:
    import requests
except ModuleNotFoundError:
    print('Could not find module requests!  Install requests using the command:\npython3 -m pip install requests')
    exit(1)

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
response = requests.get(f'https://thebluealliance.com/api/v3/event/{args.event_key}/matches',
                        headers={
                            'X-TBA-Auth-Key': args.tba_key,
                            'User-Agent': 'Schedule script'
                        })

# Handle error responses & provide context on the problem
if response.status_code != 200:
    print(f'Failed to get event information!  TBA returned status code {response.status_code}.\n{response.text}')
    exit(1)

match_information = json.loads(response.text)
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
