import os

def GetPatches(map, pwad_dir):
    dehs = []
    pwads = []
    mwads = []

    # build lists of map specific files we need to pass in
    patches = [patch for patch in map['Files'].split('|') if patch]
    for patch in patches:
        ext = os.path.splitext(patch)[1]
        if ext.lower() == ".deh":
            dehs.append(f"{pwad_dir}/{patch}")
        elif ext.lower() == ".wad":
            pwads.append(f"{pwad_dir}/{patch}")
        else:
            print(f"Ignoring unsupported file "'{patch}'"with extension '{ext}'")

    # for chocolate doom/vanilla wad merge emulation
    merges = [merge for merge in map['Merge'].split('|') if merge]
    for merge in merges:
        mwads.append(f"{pwad_dir}/{merge}")

    p = {}
    p['dehs'] = dehs
    p['pwads'] = pwads
    p['mwads'] = mwads

    return p
