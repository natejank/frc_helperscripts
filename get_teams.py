#!/usr/bin/env python3

import json
import argparse
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

args = parser.parse_args()

# Get match information.  Headers are needed to authenticate with TBA.
request = Request(
    url=f'https://thebluealliance.com/api/v3/event/{args.event_key}/teams',
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



team_information = json.loads(response.read().decode('utf-8'))
team_information.sort(key=lambda x: x['team_number'])  # sort by match number

for team in team_information:

    print(f'{team["team_number"]},{team["nickname"]}')
