#!/usr/bin/env python3
import lib.py.arguments as args
import lib.py.common as common
from lib.py.load_mods import *
from lib.py.config import LoadConfig

import os
import json
import glob

p_args = args.get_analyse_args()

config = LoadConfig(p_args.config)

mods = LoadMods(config.pwad_dir, p_args.mod_list)
maps = GetMapsFromMods(mods)

for map in maps:
    pfx = map.get_map_prefix()
    files = glob.glob(config.demo_dir + f"/{pfx}*")
    stats = []
    lumps = []
    for file in files:
        if file.endswith('STATS.json'):
            stats.append(file)
        elif file.endswith('.lmp'):
            lumps.append(file)

    for stat in stats:
        statfile = json.load(open(stat))
        if statfile['levelStats']:
            levelStats = statfile['levelStats']
            print("has levelStats")

    print("go")
 #   GetStatsForMap(map)
