import json

class Config:
    def __init__(self, raw_json):
        self.default_complevel = raw_json['default_complevel']
        # TODO defaults for these in case they're not in the JSON
        self.dsda_path = raw_json['dsda_path']
        self.dsda_cfg = raw_json['dsda_cfg']
        self.chocolatedoom_path = raw_json['chocolatedoom_path']
        self.chocolatedoom_cfg_default = raw_json['chocolatedoom_cfg_default']
        self.chocolatedoom_cfg_extra = raw_json['chocolatedoom_cfg_extra']
        if 'dsdadoom_hud_lump' in raw_json.keys():
            self.dsdadoom_hud_lump = raw_json['dsdadoom_hud_lump']
        else:
            self.dsdadoom_hud_lump = None
        self.crispydoom_path = raw_json['crispydoom_path']
        self.iwad_dir = raw_json['iwad_dir']
        self.pwad_dir = raw_json['pwad_dir']
        self.demo_dir = raw_json['demo_dir']

def LoadConfig(config_path) -> Config:
    raw = json.load(open(config_path))
    return Config(raw)
    