import re
import os
import json

# constants
LEVELSTAT_TXT = "./levelstat.txt"

def NewStats():
    _stats = {}
    _stats['map']         = ""
    _stats['compLevel']   = 0
    _stats['sourcePort']  = ""
    _stats['args']        = []
    _stats['levelStats']  = None
    return _stats

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

def WriteStats(stats, demo_dir, demo_name):
    stats_json_path = f"{demo_dir}/{demo_name}-STATS.json"

    if os.path.exists(LEVELSTAT_TXT):
        with(open(LEVELSTAT_TXT)) as raw_level_stats:
            if not os.path.exists("./tmp"):
                os.mkdir("./tmp")
            stats['levelStats'] = ParseLevelStats(raw_level_stats.read())
            archived_level_stat_txt = f"./tmp/levelstat_{demo_name}.txt"
            raw_level_stats.close()
            os.rename(LEVELSTAT_TXT, archived_level_stat_txt)
            
    else:
        print("""
    No levelstat.txt found. I assume you didn't finish the level or aren't using dsda-doom""")
    
    with(open(stats_json_path, 'w')) as j:
        json.dump(stats, j)