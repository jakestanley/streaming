#!/usr/bin/env python3
from lib.py.arguments import *
from lib.py.ui import *
from lib.py.obs import *
from lib.py.wad import *
from lib.py.patches import *
from lib.py.common import *
from lib.py.stats import *
from lib.py.launch import *

from datetime import datetime

import json
import csv
import os
import subprocess

# constants
LAST_JSON = "./last.json"

p_args = get_args()

def GetLastMap():
    if(p_args.last):
        if os.path.exists(LAST_JSON):
            with(open(LAST_JSON)) as f:
                return json.load(f)
        else:
            print("""
    Cannot select last map as 'last.json' was not found
            """)
    return None

def VerifyModListCsvHeader(reader):
    for required in required_header_names:
        if not required in reader.fieldnames:
            print(f"""
    Error: Missing required column '{required}' in header.
    Header contained '{reader.fieldnames}'
            """)
            exit(1)
    return reader;

def GetMaps():
    if(p_args.mod_list):
        try:
            _csv = open(p_args.mod_list)
        except FileNotFoundError:
            print(f"""
    Error: Could not find file 
        '{p_args.mod_list}'
            """)
            exit(1)
        verified = VerifyModListCsvHeader(csv.DictReader(_csv))
        return GetMapsFromModList(verified, config['pwad_dir'])
    else:
        print("""
    Error. No mod list provided. Maybe I should just launch Doom?
        """)
        parser.print_usage()
        exit(1)

def GetMapNameString(map):
    return f"#{map['Ranking']}: {map['Title']} | {map['Author']} | {map['Map']}"

_json = open(p_args.config) 
config = json.load(_json) 
lc = GameConfig(config)
stats = NewStats()

obsController = ObsController(not p_args.no_obs)
obsController.Setup()

map = GetLastMap()
if(not map):
    maps = GetMaps()
    if(p_args.random):
        import random
        map = random.choice(maps)
    else:
        map = OpenMapSelection(maps)
        with open('last.json', 'w') as f:
            json.dump(map, f)

if(not map):
    print("no map was selected")
    exit(1)

# set default doom arguments
lc.set_comp_level(map['CompLevel'] or config['default_complevel'])

mapId = map['Map']
stats['map'] = mapId

# TODO consider set_map in GameConfig
if IsDoom1(mapId):
    warp = GetDoom1Warp(mapId)
    lc.set_iwad("DOOM")
elif IsDoom2(mapId):
    warp = GetDoom2Warp(mapId)
    lc.set_iwad("DOOM2")
else:
    print(f"Unsupported map ID '{mapId}'")
    exit(1)

lc.set_warp(warp)
lc.set_map_id(mapId)

patches = GetPatches(map, config['pwad_dir'])
lc.set_dehs(patches['dehs'])
lc.set_pwads(patches['pwads'])
lc.set_mwads(patches['mwads'])

obsController.UpdateMapTitle(map['Title'])

# set the demo name. even if we don't record a demo, we use this to save stats
# YYYY-MM-DDTHH:MM:SS
timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")

# record the demo
lc.set_record_demo(not p_args.no_demo)

if map['Port'] == 'chocolate':

    doom_args = lc.build_chocolate_doom_args()

    # TODO: fix as this is a switch param, not in config
    if(config['crispy']):
        stats['sourcePort'] = "crispy"
        executable = config['crispydoom_path']
    else:
        stats['sourcePort'] = "chocolate"
        executable = config['chocolatedoom_path']
else:

    doom_args = lc.build_dsda_doom_args()

    stats['compLevel'] = lc.get_comp_level()
    stats['sourcePort'] = "dsdadoom"

    executable = config['dsda_path']

print(f"""
    Starting with the following arguments:
        {doom_args}""")

command = [executable]
command.extend(doom_args)
stats['args'] = doom_args

demo_name = lc.get_demo_name()

obsController.SetScene('Playing')
if p_args.auto_record:
    obsController.StartRecording()

running = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if p_args.auto_record:
    obsController.StopRecording(demo_name)

obsController.SetScene('Waiting')

WriteStats(stats, config['demo_dir'], demo_name)