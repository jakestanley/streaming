import re
import os
import json

from lib.py.launch import LaunchConfig

# constants
LEVELSTAT_TXT = "./levelstat.txt"

def ParseLevelStats(rawLevelStats):

    levelStats = {}
    levelStats['Time'] = "???"
    levelStats['Kills'] = "???"
    levelStats['Secrets'] = "???"
    levelStats['Items'] = "???"

    regex_time = '(\d+:\d+\.\d+)'
    mtch = re.search(regex_time, rawLevelStats)
    if re.search(regex_time, rawLevelStats):
        levelStats['Time'] = re.search(regex_time, rawLevelStats).group(1)

    regex_kills = 'K: (\d+\/\d+)'
    if re.search(regex_kills, rawLevelStats):
        levelStats["Kills"] = re.search(regex_kills, rawLevelStats).group(1)

    regex_secrets = 'S: (\d+\/\d+)'
    if re.search(regex_secrets, rawLevelStats):
        levelStats["Secrets"] = re.search(regex_secrets, rawLevelStats).group(1)

    regex_items = 'I: (\d+\/\d+)'
    if re.search(regex_items, rawLevelStats):
        levelStats["Items"] = re.search(regex_items, rawLevelStats).group(1)

    return levelStats

class Statistics:
    def __init__(self, launch: LaunchConfig, demo_dir: str):
        self._stats = {}
        self._stats['compLevel']    = launch.get_comp_level()
        self._stats['sourcePort']   = launch.get_port()
        self._stats['command']      = launch.get_command()
        self._stats['levelStats']   = None
        self._launch = launch
        self._demo_dir = demo_dir

    def set_level_stats(self):
        if os.path.exists(LEVELSTAT_TXT):
            with(open(LEVELSTAT_TXT)) as raw_level_stats:
                if not os.path.exists("./tmp"):
                    os.mkdir("./tmp")
                self._stats['levelStats'] = ParseLevelStats(raw_level_stats.read())
                archived_level_stat_txt = f"./tmp/levelstat_{self._launch.get_demo_name()}.txt"
            raw_level_stats.close()
            os.rename(LEVELSTAT_TXT, archived_level_stat_txt)
        else:
            print("""
                No levelstat.txt found. I assume you didn't finish the level 
                or aren't using dsda-doom""")

    def write_stats(self):
        stats_json_path = f"{self._demo_dir}/{self._launch.get_demo_name()}-STATS.json"
        with(open(stats_json_path, 'w')) as j:
            json.dump(self._stats, j)
