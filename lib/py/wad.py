import subprocess
import os
import re

def GetMapsFromModList(rows, pwad_dir):
    regex_mapentries = '(E\dM\d|MAP\d\d|MAPINFO)'
    maps = []
    for row in rows:
        files = [patch for patch in row['Files'].split('|') if patch]
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
                        map = row.copy()
                        # TODO separate map name and wad title so we can have a caption format like Sunlust MAP02: Down Through
                        map['Map'] = mapentry[0]
                        map['MapName'] = mapentry[1]
                        maps.append(map)
                else:
                    mapentries.sort()
                    for mapentry in mapentries:
                        map = row.copy()
                        map['Map'] = mapentry
                        maps.append(map)

    return maps