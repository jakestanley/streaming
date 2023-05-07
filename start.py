#!/usr/bin/env python3
from simple_term_menu import TerminalMenu
from datetime import datetime

import obsws_python as obs
import json
import csv
import re
import os
import time

def getMapNameString(map):
    return f"#{map['Ranking']}: {map['Title']} | {map['Author']} | {map['Map']}"

_json = open('./config-mac.json') 
config = json.load(_json) 

_csv = open("./Season1.csv")
_csv_reader = csv.DictReader(_csv)

maps = []
options = []
for row in _csv_reader:
    maps.append(row)
    options.append(getMapNameString(row))

terminal_menu = TerminalMenu(options)
index = terminal_menu.show()
if index == None:
    print("Nothing selected. Exiting")
    exit(0)

# default arguments
complevel = maps[index]['CompLevel'] or config['default_complevel']
args = '-nomusic -skill 4'

# default
demo_prefix = ""
demo_name = ""

mapId = maps[index]['Map']
DOOM_regex=r'^E(\d)M(\d)$'
DOOM2_regex=r'^MAP(\d+)$'

if re.match(DOOM_regex, mapId):
    print("Detected a Doom map string")
    demo_prefix="DOOM" # default just in case no pwad is provided
    episodeno = int(re.match(DOOM_regex, mapId).group(1))
    mapno =     int(re.match(DOOM_regex, mapId).group(2))
    args += f"-warp {episodeno} {mapno} "
    args += f"-iwad {config['iwad_dir']}/DOOM.wad "
elif re.match(DOOM2_regex, maps[index]['Map']):
    print("Detected a Doom II map string")
    demo_prefix="DOOM2" # default just in case no pwad is provided
    mapno = int(re.match(DOOM2_regex, mapId).group(1))
    args += f"-warp {mapno} "
    args += f"-iwad {config['iwad_dir']}/DOOM2.wad "
else:
    print(f"Could not parse Map value: {maps[index]['Map']}")
    exit(1)

dehs = []
pwads = []
mwads = []

# build lists of map specific files we need to pass in
patches = [patch for patch in maps[index]['Files'].split('|') if patch]
for patch in patches:
    ext = os.path.splitext(patch)[1]
    if ext.lower() == ".deh":
        dehs.append(f"{config['pwad_dir']}/{patch}")
    elif ext.lower() == ".wad":
        pwads.append(f"{config['pwad_dir']}/{patch}")
    else:
        print(f"Ignoring unsupported file "'{patch}'"with extension '{ext}'")

# for chocolate doom/vanilla wad merge emulation
merges = [merge for merge in maps[index]['Merge'].split('|') if merge]
for merge in merges:
    mwads.append(f"{config['pwad_dir']}/{merge}")

if len(dehs) > 0:
    args += "-deh "
    for deh in dehs:
        args += f"{deh} "

if len(pwads) > 0:
    args += "-file "
    demo_prefix = os.path.splitext(os.path.basename(pwads[0]))[0]
    for pwad in pwads:
        args += f"{pwad} "

# set map title in OBS (TODO)
## SetInputSettings

# record the demo
timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")
arg_record = f"-record {config['demo_dir']}/{demo_prefix}-{mapId}-{timestr}.lmp "
args += arg_record

if maps[index]['Port'] == 'chocolate':
    print("Starting chocolate-doom with the following arguments:")
    if len(merges) > 0:
        args += "-merge "
        for merge in merges:
            args += f"{merge} "

    args += f"-config {config['chocolatedoom_cfg_default']} -extraconfig {config['chocolatedoom_cfg_extra']} "
    executable = config['chocolatedoom_path']
else:
    print("Starting dsda-doom with the following arguments:")
    executable = config['dsda_path']

print(args)
time.sleep(3)

# TODO: SetCurrentProgramScene("Playing")
# TODO: start process with args and wait for exit
# TODO: SetCurrentProgramScene

exit(0)
cl = obs.ReqClient(host='localhost', port=4455, password='')

cur_scene = cl.get_current_program_scene()
print("This scene: " + cur_scene.current_program_scene_name)
