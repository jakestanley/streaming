import csv
from lib.py.patches import *

def GetMaps():
    return None

def VerifyModListCsvHeader(path_to_mod_list_csv):
    return None


def LoadMods(pwad_dir, path_to_mod_list_csv) -> list:

    # VerifyModListCsvHeader(path_to_mod_list_csv)
    mod_list = csv.DictReader(open(path_to_mod_list_csv))

    mods = []
    for raw_mod in mod_list:
        mod = LoadMod(pwad_dir, raw_mod['Season'], raw_mod['Ranking'], 
                      raw_mod['Title'], raw_mod['Author'],  raw_mod['IWAD'], 
                      raw_mod['Files'], raw_mod['Port'], raw_mod['Merge'], 
                      raw_mod['CompLevel'])

        mods.append(mod)

    return mods

def LoadMod(pwad_dir, season, ranking, title, author, iwad, files, port, merge, complevel) -> Mod:

    dehs = []
    pwads = []
    mwads = []

    # build lists of map specific files we need to pass in
    patches = [patch for patch in files.split('|') if patch]
    for patch in patches:
        ext = os.path.splitext(patch)[1]
        path = os.path.join(pwad_dir, patch)
        if ext.lower() == ".deh":
            dehs.append(path)
        elif ext.lower() == ".wad":
            pwads.append(path)
        else:
            print(f"Ignoring unsupported file "'{patch}'"with extension '{ext}'")

    # for chocolate doom/vanilla wad merge emulation
    merges = [merge for merge in merge.split('|') if merge]
    for merge in merges:
        mwads.append(os.path.join(pwad_dir, merge))

    mod = Mod(season = season, ranking = ranking, title = title, author = author, iwad = iwad, 
              dehs = dehs, pwads = pwads, mwads = mwads)
    mod.load_maps(pwad_dir)

    return mod