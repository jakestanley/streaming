#!/usr/bin/env python3

import subprocess
import json

import lib.py.arguments as args
from lib.py.mod import *
from lib.py.load_mods import *
from lib.py.config import *
from lib.py.launch import LaunchConfig
from lib.py.obs import *
from lib.py.ui.mapselect import OpenMapSelection
from lib.py.ui.options import OpenOptionsGui
from lib.py.last import *
from lib.py.stats import Statistics

def GetMapsFromMods(mods):
    maps = []
    for mod in mods:
        maps.extend(mod.maps)

    return maps

p_args = args.get_args()

config = LoadConfig(p_args.config)

if(not p_args.no_gui):
    p_args = OpenOptionsGui(p_args)

launch = LaunchConfig(config)

obsController = ObsController(not p_args.no_obs)
obsController.Setup()

map = None
if(p_args.last):
    map = GetLastMap()

if(not map):
    mods = LoadMods(config.pwad_dir, p_args.mod_list)
    maps = GetMapsFromMods(mods)
    if(p_args.random):
        import random
        map = random.choice(maps)
    else:
        # TODO flatten map list and get index
        map = OpenMapSelection(maps)
        SaveSelectedMap(map)
        # TODO consider implementing this??? consider implementing saving all command line args as config
        #SaveSelectedModList(p_args.mod_list)

if(not map):
    exit(0)

launch.set_map(map)
demo_name = launch.get_demo_name()
command = launch.get_command()

obsController.SetScene('Playing')
if p_args.auto_record:
    obsController.StartRecording()

statistics = Statistics(launch, config.demo_dir)
running = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# update stats and save
statistics.set_level_stats()
statistics.write_stats()

if p_args.auto_record:
    obsController.StopRecording(demo_name)

# TODO setting for waiting scene
obsController.SetScene('Waiting')
