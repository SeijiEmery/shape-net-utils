#!/usr/bin/env python
import sys
import platform
import subprocess

WIN_BLENDER_INSTALL_PATH = 'blender'

def run_blender_script (script):
    """ Runs a blender script from the commandline using the user's blender install """

    if platform.system().lower() == 'windows':
        blender_path = WIN_BLENDER_INSTALL_PATH
    else:
        blender_path = 'blender'
    subprocess.run([ blender_path, '-b', '-P', script ])

if __name__ == '__main__':
    try:
        _, script = sys.argv
        run_blender_script(script)
    except ValueError:
        print("Usage: %s <script>.py"%(sys.argv[0]))
