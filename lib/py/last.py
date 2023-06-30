import os
import json
import jsonpickle

from lib.py.mod import Map

# constants
LAST_JSON = "./last.json"

def GetLastMap() -> Map:
    if os.path.exists(LAST_JSON):
        with(open(LAST_JSON)) as f:
            return jsonpickle.decode(json.load(f))
    else:
        print("""
Cannot select last map as '{LAST_JSON}' was not found
        """)
        return None

def SaveSelectedMap(map: Map):
    # saves selected map for last
    with open(LAST_JSON, 'w') as f:
        json.dump(jsonpickle.encode(map), f)
