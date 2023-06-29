import argparse

parser = argparse.ArgumentParser()

def _get_common_args():
    parser.add_argument("-c",  "--config",      type=str,               help="Path to script configuration file", default=".\examples\config.json")
    parser.add_argument("-ml", "--mod-list",    type=str,               help="Mod list")
    parser.add_argument("-g", "--no-gui",       action='store_true',    help="Command line operation only")

def get_args():
    _get_common_args()
    parser.add_argument("-no", "--no-obs",      action='store_true',    help="Disable OBS control")
    parser.add_argument("-nq", "--no-qol",      action='store_true',    help="Disable QoL mods (use this if you are experiencing issues)")
    parser.add_argument("-ps", "--play-scene",  type=str,               help="Which scene should OBS switch to when game starts")
    parser.add_argument("-sp", "--source-port", type=str,               help="Override source port (force)")
    parser.add_argument("-rr", "--re-record",   action='store_true',    help="Re-record a completed demo")
    parser.add_argument("-ar", "--auto-record", action='store_true',    help="Automatically record and stop when gameplay ends")
    parser.add_argument("-r",  "--random",      action='store_true')
    parser.add_argument("-nd", "--no-demo",     action='store_true',    help="Demo recording will be disabled")
    parser.add_argument("-cr", "--crispy",      action='store_true',    help="Use Crispy Doom instead of Chocolate Doom")
    parser.add_argument("-l",  "--last",        action='store_true',    help="If saved, play last map")

    args = parser.parse_args()

    return args

def get_analyse_args():
    _get_common_args()
    
    args = parser.parse_args()

    return args
