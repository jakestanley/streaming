import lib.py.wad as wad

import csv

required_header_names = ['Season','Ranking','Title','Author','Notes','DoomWiki','IWAD','Files','Port','Merge','CompLevel']
column_order = ['Season', 'Ranking', 'Title', 'Map', 'MapName', 'IWAD', 'Files', 'Merge', 'Port', 'CompLevel', 'DoomWiki', 'Notes']

def VerifyModListCsvHeader(reader):
    for required in required_header_names:
        if not required in reader.fieldnames:
            print(f"""
    Error: Missing required column '{required}' in header.
    Header contained '{reader.fieldnames}'
            """)
            exit(1)
    return reader;

def GetMaps(mod_list, pwad_dir):
    if(mod_list):
        try:
            _csv = open(mod_list)
        except FileNotFoundError:
            print(f"""
    Error: Could not find file 
        '{mod_list}'
            """)
            exit(1)
        verified = VerifyModListCsvHeader(csv.DictReader(_csv))
        return wad.GetMapsFromModList(verified, pwad_dir)
    else:
        print("""
    Error. No mod list provided. Maybe I should just launch Doom?
        """)
        exit(1)