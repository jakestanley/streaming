import os
import subprocess
import re

regex_mapentries = '(E\dM\d|MAP\d\d|MAPINFO)'
regex_warp = r'E(\d)M(\d)|MAP(\d{2})'

# TODO consider partially constructing only and doing 
#   the rest (i.e default comp level) in LoadMods
class Mod:
    def __init__(self, title, author, ranking = 0, season = "", complevel = None, iwad = None, port = None, dehs=[], pwads=[], mwads=[]):
        self.title = title
        self.author = author
        self.season = season
        self.ranking = ranking
        self.complevel = complevel
        # TODO if not provided, assume from maps or WAD header
        self.iwad = iwad
        self.port = port
        self.dehs = dehs
        self.pwads = pwads
        self.mwads = mwads
        self.maps = []

    def get_mapinfo_lumps(self, pwad_dir) -> list:
        mapinfo_lumps: list(str) = []

        for file in self._pwads+self._mwads:
            wadread = f"wad-read {pwad_dir}/{file} MAPINFO"

    def get_mod_prefix(self):
        if len(self.pwads) > 0:
            demo_prefix = os.path.splitext(os.path.basename(self.pwads[0]))[0]
        elif len(self.mwads) > 0:
            demo_prefix = os.path.splitext(os.path.basename(self.mwads[0]))[0]
        elif len(self.dehs) > 0:
            demo_prefix = os.path.splitext(os.path.basename(self.dehs[0]))[0]
        else:
            demo_prefix = self._iwad

    def load_maps(self, pwad_dir):

        #mapinfo_lumps: list(str) = get_mapinfo_lumps()
        files = self.pwads + self.mwads

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext.lower() == ".wad":
                wadls = f"wad-ls {file}"
                output = subprocess.check_output(wadls, shell=True, universal_newlines=True)
                mapentries = list(set(re.findall(regex_mapentries, output)))
                if "MAPINFO" in mapentries:
                    wadread = f"wad-read {pwad_dir}/{file} MAPINFO"
                    output = subprocess.check_output(wadread, shell=True, universal_newlines=True)
                    mapentries = re.findall("(E\dM\d|MAP\d\d) \"(.*)\"", output)
                    for mapentry in mapentries:
                        self.maps.append(Map(mapentry[0], self, mapentry[1]))
                else:
                    mapentries.sort()
                    for mapentry in mapentries:
                        self.maps.append(Map(mapentry, self))

class Map:
    def __init__(self, id, mod:Mod=None, title=None):
        self.id = id
        self.mod = mod
        self._title = title
    
    def get_title(self):
        if self._title:
            return self._title
        return self.id

    def get_map_prefix(self):
        return f"{self.mod.get_mod_prefix()}-{self.id}"

    def get_warp(self):
        warp = []
        for group in re.match(regex_warp, self.id).groups():
            if group:
                # converts "01" to 1 then back to "1" cz i'm lazy
                warp.append(str(int(group)))
        return warp
