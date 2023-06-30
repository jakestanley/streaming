#!/usr/bin/env python3
from lib.py.arguments import *
import lib.py.common as common

import os
import json

# TODO consider making this a member of `Map`
def GetDemoSearchPrefix(map):
    return f"{map.Map}-"


p_args = get_analyse_args()

config = json.load(open(p_args.config))

if p_args.mod_list:
    print("Mod list provided. Will restrict analysis to these mods")
    maps = common.GetMaps(p_args.mod_list, config['pwad_dir'])

    for map in maps:
        print(GetDemoSearchPrefix(map))


        print(map)
        # TODO get demo prefix 
else:
    print("Analysing all demos")
