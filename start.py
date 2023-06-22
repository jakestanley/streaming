#!/usr/bin/env python3
from lib.py.arguments import *
from lib.py.ui import *
from lib.py.obs import *
from lib.py.wad import *
from lib.py.patches import *
from lib.py.common import *

from datetime import datetime

import json
import csv
import re
import os
import time
import subprocess

p_args = get_args()

def GetLastMap():
    if(p_args.last):
        if os.path.exists("./last.json"):
            with(open("./last.json")) as f:
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
doom_args = []
complevel = map['CompLevel'] or config['default_complevel']
doom_args.extend(['-nomusic', '-skill', '4'])

# default
demo_prefix = ""
demo_name = ""

mapId = map['Map']

if IsDoom1(mapId):
    warp = GetDoom1Warp(mapId)
    demo_prefix="DOOM" # default just in case no pwad is provided
    iwadpath = f"{config['iwad_dir']}/DOOM.wad"
elif IsDoom2(mapId):
    warp = GetDoom2Warp(mapId)
    demo_prefix="DOOM2" # default just in case no pwad is provided
    iwadpath = f"{config['iwad_dir']}/DOOM2.wad"
else:
    print(f"Unsupported map ID '{mapId}'")
    exit(1)

doom_args.extend(['-iwad', iwadpath])
doom_args.extend(['-warp', warp])

patches = GetPatches(map, config['pwad_dir'])

if len(patches['dehs']) > 0:
    doom_args.append("-deh")
    doom_args.extend(patches['dehs'])

if len(patches['pwads']) > 0:
    doom_args.append("-file")
    # use first pwad name as demo prefix
    demo_prefix = os.path.splitext(os.path.basename(patches['pwads'][0]))[0]
    doom_args.extend(patches['pwads'])

obsController.UpdateMapTitle(map['Title'])

# set the demo name. even if we don't record a demo, we use this to save stats
# YYYY-MM-DDTHH:MM:SS
timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")
demo_name = f"{demo_prefix}-{mapId}-{timestr}"

# record the demo
if (not p_args.no_demo):
    doom_args.append("-record")
    doom_args.append(f"{config['demo_dir']}/{demo_name}.lmp")

if map['Port'] == 'chocolate':
    if len(patches['merges']) > 0:
        doom_args.append("-merge")
        doom_args.extend(patches['merges'])

    doom_args.extend(["-config", config['chocolatedoom_cfg_default'], "-extraconfig", config['chocolatedoom_cfg_extra']])

    if(config['crispy']):
        executable = config['crispydoom_path']
    else:
        executable = config['chocolatedoom_path']
else:
    print(f"""
    Starting dsda-doom with the following arguments:
        {doom_args}      
    """)
    doom_args.extend(['-complevel', complevel, '-window'])
    executable = config['dsda_path']

command = [executable]
command.extend(doom_args)

obsController.SetScene('Playing')
if p_args.auto_record:
    obsController.StartRecording()

running = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if p_args.auto_record:
    obsController.StopRecording(demo_name)

obsController.SetScene('Waiting')
