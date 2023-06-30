#!/usr/bin/env python3
from lib.py.arguments import *
from lib.py.ui.mapselect import *
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

# TODO: must return a `Map` instance or None
def GetLastMap():
    if(p_args.last):
        if os.path.exists(LAST_JSON):
            with(open(LAST_JSON)) as f:
                return json.load(f)
        else:
            print("""
    Cannot select last map as '{LAST_JSON}' was not found
            """)
    return None

# TODO make this a member of `Map`
def GetMapNameString(map):
    return f"#{map['Ranking']}: {map['Title']} | {map['Author']} | {map['Map']}"

p_args = get_args()
config = json.load(open(p_args.config)) 
lc = LaunchConfig(config)
stats = NewStats()

obsController = ObsController(not p_args.no_obs)
obsController.Setup()

# TODO must return a `Map`
# Get map to be played
map = GetLastMap()
if(not map):
    mods = GetMods(p_args.mod_list, config['pwad_dir'])
    maps = GetMaps(p_args.mod_list, config['pwad_dir'])
    if(p_args.random):
        import random
        map = random.choice(maps)
    else:
        map = OpenMapSelection(maps)
        # saves selected map for last
        with open(LAST_JSON, 'w') as f:
            json.dump(map, f)

if(not map):
    print("no map was selected")
    exit(1)

lc.set_map(map)

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

obsController.UpdateMapTitle(map['Title'])

# set the demo name. even if we don't record a demo, we use this to save stats
# YYYY-MM-DDTHH:MM:SS
timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")

# record the demo
lc.set_record_demo(not p_args.no_demo)

if map['Port'] == 'chocolate':

    doom_args = lc.build_chocolate_doom_args()

    # TODO: fix as this is a switch param, not in config
    if(p_args.crispy):
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
