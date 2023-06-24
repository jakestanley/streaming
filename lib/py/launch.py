import os
from datetime import datetime

DEFAULT_SKILL = 4

class GameConfig:
    def __init__(self, config):
        self._script_config = config
        self._timestr = None
        self._pwads = []
        self._dehs = []
        self._mwads = []
        self._map_id = ""
        self._warp = []
        self._iwad = ""
        self._file = ""
        self._record_demo = True
        self._config = ""
        self._extra_config = ""
        self._skill = DEFAULT_SKILL
        self._no_music = True
        self._comp_level = 0
        self._window = True
        self._demo_prefix = ""

    def build_chocolate_doom_args(self):
        
        choccy_args = self.build_args()

        if len(self._mwads) > 0:
            choccy_args.append("-merge")
            choccy_args.extend(self._mwads)

        choccy_args.extend(["-config", self._script_config['chocolatedoom_cfg_default']])
        choccy_args.extend(["-extraconfig", self._script_config['chocolatedoom_cfg_extra']])

        return choccy_args
    
    def build_dsda_doom_args(self):

        dsda_args = self.build_args()

        dsda_args.extend(['-complevel', self._comp_level, '-window', '-levelstat'])

        return dsda_args

    def build_args(self):

        doom_args = []

        if len(self._dehs) > 0:
            doom_args.append("-deh")
            doom_args.extend(self._dehs)

        if len(self._pwads) > 0:
            doom_args.append("-file")
            doom_args.extend(self._pwads)

        doom_args.extend(['-iwad', f"{self._script_config['iwad_dir']}/{self._iwad}.wad"])
        doom_args.extend(['-warp'])
        doom_args.extend(self._warp)

        if self._record_demo:
            doom_args.append("-record")
            doom_args.append(f"{self._script_config['demo_dir']}/{self.get_demo_name()}.lmp")

        if self._no_music:
            doom_args.append('-nomusic')

        doom_args.extend(['-skill', f"{self._skill}"])

        return doom_args

    # demo_prefix
    def set_demo_prefix(self, demo_prefix):
        self._demo_prefix = demo_prefix

    def get_demo_prefix(self):
        return self._demo_prefix
    
    # demo_name
    def get_demo_name(self):
        if self._timestr == None:
            self._timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")

        if len(self._pwads) > 0:
            demo_prefix = os.path.splitext(os.path.basename(self._pwads[0]))[0]
        else:
            demo_prefix = self._iwad

        return f"{demo_prefix}-{self._map_id}-{self._timestr}"

    # pwads
    def set_pwads(self, pwads):
        self._pwads = pwads

    def get_pwads(self):
        return self._pwads
    
    # dehs
    def set_dehs(self, dehs):
        self._dehs = dehs

    def get_dehs(self):
        return self._dehs
    
    # merges
    def set_mwads(self, merges):
        self._mwads = merges

    def get_mwads(self):
        return self._mwads

    # warp # TODO consider set_map_id instead and infer that
    def set_warp(self, warp):
        self._warp = warp

    def get_warp(self):
        return self._warp

    # iwad
    def set_iwad(self, iwad):
        self._iwad = iwad

    def get_iwad(self):
        return self._iwad

    # file
    def set_file(self, file):
        self._file = file

    def get_file(self):
        return self._file

    # record_demo
    def set_record_demo(self, record_demo):
        self._record_demo = record_demo

    def get_record_demo(self):
        return self._record_demo

    # config
    def set_config(self, config):
        self._config = config

    def get_config(self):
        return self._config

    # extra_config
    def set_extra_config(self, extra_config):
        self._extra_config = extra_config

    def get_extra_config(self):
        return self._extra_config

    # skill
    def set_skill(self, skill):
        self._skill = skill

    def get_skill(self):
        return self._skill

    # no_music
    def set_no_music(self, no_music):
        self._no_music = no_music

    def get_no_music(self):
        return self._no_music

    # comp_level
    def set_comp_level(self, comp_level):
        self._comp_level = comp_level

    def get_comp_level(self):
        return self._comp_level

    # window
    def set_window(self, window):
        self._window = window

    def get_window(self):
        return self._window

    # map_id
    def set_map_id(self, map_id):
        self._map_id = map_id

    def get_map_id(self):
        return self._map_id
