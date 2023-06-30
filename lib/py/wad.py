import subprocess
import os
import re
from lib.py.patches import *
from lib.py.mod import *

regex_mapentries = '(E\dM\d|MAP\d\d|MAPINFO)'
DOOM_regex=r'^E(\d)M(\d)$'
DOOM2_regex=r'^MAP(\d+)$'

def IsDoom1(mapId):
    return re.match(DOOM_regex, mapId)

def IsDoom2(mapId):
    return re.match(DOOM2_regex, mapId)

def GetDoom1Warp(mapId):
    episodeno = (re.match(DOOM_regex, mapId).group(1))
    mapno =     (re.match(DOOM_regex, mapId).group(2))
    return [episodeno, mapno]

def GetDoom2Warp(mapId):
    map = re.match(DOOM2_regex, mapId).group(1)
    return [f"{int(map)}"]

def GetModsFromModsList(verified, pwad_dir):
    return None

def GetMapsForMod(mod: Mod, pwad_dir):
    maps = []
    files = [patch for patch in mod['Files'].split('|') if patch]
    for file in files:
        ext = os.path.splitext(file)[1]
        if ext.lower() == ".wad":
            wadls = f"wad-ls {pwad_dir}/{file}"
            output = subprocess.check_output(wadls, shell=True, universal_newlines=True)
            mapentries = list(set(re.findall(regex_mapentries, output)))
            if "MAPINFO" in mapentries:
                wadread = f"wad-read {pwad_dir}/{file} MAPINFO"
                output = subprocess.check_output(wadread, shell=True, universal_newlines=True)
                mapentries = re.findall("(E\dM\d|MAP\d\d) \"(.*)\"", output)
                for mapentry in mapentries:
                    map = mod.copy()
                    map['Map'] = mapentry[0]
                    map['MapName'] = mapentry[1]
                    maps.append(map)
            else:
                mapentries.sort()
                for mapentry in mapentries:
                    map = mod.copy()
                    map['Map'] = mapentry
                    map['MapName'] = ""
                    maps.append(map)

    return maps


def GetMapsFromModList(rows, pwad_dir):
    
    maps = []
    for row in rows:
        maps.extend(GetMapsForMod(row, pwad_dir))

    return maps