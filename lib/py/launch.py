import os
from lib.py.config import Config
from datetime import datetime

ULTRA_VIOLENCE = 4
DEFAULT_SKILL = ULTRA_VIOLENCE

class LaunchConfig:
    def __init__(self, config):
        self._script_config: Config = config
        self._timestr = None
        self._map = None
        self._file = ""
        self._config = ""
        self._extra_config = ""
        self._skill = DEFAULT_SKILL
        self._no_music = True
        self._comp_level = None
        self._window = True
        self._demo_prefix = ""
        self._port_override = None

    def get_comp_level(self):
        # initialise final comp level only
        final_comp_level = 9

        # if comp level has been overridden
        if self._comp_level:
            final_comp_level = self._comp_level
        # or if map has a comp level
        elif self._map.mod.complevel:
            final_comp_level = self._map.get_mod().get_comp_level()
        # or use default comp level
        else:
            final_comp_level = int(self._script_config.default_complevel)

        return final_comp_level

    def build_chocolate_doom_args(self):
        
        choccy_args = self.build_args()

        if len(self._map.mod.mwads) > 0:
            choccy_args.append("-merge")
            choccy_args.extend(self._map.mod.mwads)

        choccy_args.extend(["-config", self._script_config['chocolatedoom_cfg_default']])
        choccy_args.extend(["-extraconfig", self._script_config['chocolatedoom_cfg_extra']])

        return choccy_args
    
    def build_dsda_doom_args(self):

        dsda_args = self.build_args()

        final_comp_level = self.get_comp_level()

        dsda_args.extend(['-complevel', str(final_comp_level)])
        # the usual
        dsda_args.extend(['-window', '-levelstat'])

        if self._script_config.dsdadoom_hud_lump:
            dsda_args.extend(['-hud', self._script_config.dsdadoom_hud_lump])

        dsda_args.extend(['-config', self._script_config.dsda_cfg])

        return dsda_args

    def build_args(self):

        # TODO: add qol mods
        doom_args = []

        if len(self._map.mod.dehs) > 0:
            doom_args.append("-deh")
            doom_args.extend(self._map.mod.dehs)

        if len(self._map.mod.pwads) > 0:
            doom_args.append("-file")
            doom_args.extend(self._map.mod.pwads)

        # TODO consider class for handling getting different types of wads instead of passing this around
        if self._map.mod.iwad:
            doom_args.extend(['-iwad', os.path.join(self._script_config.iwad_dir, self._map.mod.iwad)])
        else:
            doom_args.extend(['-iwad', os.path.join(self._script_config.iwad_dir, self._map.get_inferred_iwad())])
        
        doom_args.extend(['-warp'])
        doom_args.extend(self._map.get_warp())

        if self._script_config:
            doom_args.append("-record")
            doom_args.append(os.path.join(self._script_config.demo_dir, self.get_demo_name() + ".lmp"))

        if self._no_music:
            doom_args.append('-nomusic')

        doom_args.extend(['-skill', f"{self._skill}"])

        return doom_args

    def set_map(self, map):
        self._map = map

    def get_map(self):
        return self._map
    
    # demo_name
    def get_demo_name(self):
        if self._timestr == None:
            self._timestr = datetime.now().strftime("%Y-%m-%dT%H%M%S")

        map_prefix = self._map.get_map_prefix()
        return f"{map_prefix}-{self._timestr}"

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

    def set_port_override(self, port):
        self._port_override = port

    def get_port(self):

        # default port
        final_port = "dsdadoom"
        if (self._port_override):
            final_port = self._port_override
        elif (self._map.mod.port):
            final_port = self._map.mod.port

        # TODO if crispy override set.
        # port_override > crispy override > chocolate
        if final_port == "chocolate" and self._port_override == None:
            if self._script_config.crispy:
                final_port = "crispy"
            else:
                final_port = "chocolate"

        return final_port

    def get_command(self):
        # still TODO: stats
        port = self.get_port()

        command = []
        if port in ["chocolate", "crispy"]:
            if port == ["chocolate"]:
                command.append(self._script_config.chocolatedoom_path)
            else:
                command.append(self._script_config.crispydoom_path)
            command.extend(self.build_chocolate_doom_args())
        elif port == "dsdadoom":
            command.append(self._script_config.dsda_path)
            command.extend(self.build_dsda_doom_args())

        return command