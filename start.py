#!/usr/bin/env python3
from lib.py.arguments import *
from lib.py.ui import *
from lib.py.obs import *
from lib.py.wad import *
from lib.py.patches import *

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
        # TODO check if file exists
        # TODO save last map on complete
        return open("./last.json")
    return None

def GetMaps():
    if(p_args.mod_list):
        _csv = open(p_args.mod_list)
        return GetMapsFromModList(csv.DictReader(_csv), config['pwad_dir'])
    elif(p_args.map_list):
        _csv = open(p_args.map_list)
        return csv.DictReader(_csv)
    else:
        # TODO exception? proper error? throw?
        print("Error. No map source could be obtained. Maybe I'll just launch Doom?")
        exit(1)

def GetMapNameString(map):
    return f"#{map['Ranking']}: {map['Title']} | {map['Author']} | {map['Map']}"

def GetMapSelection(maps):
    if (p_args.last):
        open("./last.json")
        # TODO: load last map
    else:
        return OpenMapSelection(maps)

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
        map = GetMapSelection(maps)

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
DOOM_regex=r'^E(\d)M(\d)$'
DOOM2_regex=r'^MAP(\d+)$'

if re.match(DOOM_regex, mapId):
    print("Detected a Doom map string")
    demo_prefix="DOOM" # default just in case no pwad is provided
    episodeno = (re.match(DOOM_regex, mapId).group(1))
    mapno =     (re.match(DOOM_regex, mapId).group(2))
    doom_args.extend(['-warp', episodeno, mapno])
    doom_args.extend(['-iwad', f"{config['iwad_dir']}/DOOM.wad"])
elif re.match(DOOM2_regex, map['Map']):
    print("Detected a Doom II map string")
    demo_prefix="DOOM2" # default just in case no pwad is provided
    mapno = (re.match(DOOM2_regex, mapId).group(1))
    doom_args.extend(['-warp', mapno])
    doom_args.extend(['-iwad', f"{config['iwad_dir']}/DOOM2.wad"])
else:
    print(f"Could not parse Map value: {map['Map']}")
    exit(1)

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

# record the demo
if (not config['no_demo']):
    # TODO may need to use for other stuff so consider moving it out of this block?
    timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    doom_args.append("-record")
    doom_args.append(f"{config['demo_dir']}/{demo_prefix}-{mapId}-{timestr}.lmp")

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
    print("Starting dsda-doom with the following arguments:")
    doom_args.extend(['-complevel', complevel, '-window'])
    executable = config['dsda_path']

command = [executable]
command.extend(doom_args)

obsController.SetScene('Playing')
running = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# TODO stop recording and move file
obsController.SetScene('Waiting')
