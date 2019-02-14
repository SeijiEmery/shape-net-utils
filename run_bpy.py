#!/usr/bin/env python
import sys
import platform
import subprocess

WIN_BLENDER_INSTALL_PATH = 'blender'        # Set this if you're a windows user

def run_blender_script (script, *args):
    """ Runs a blender script from the commandline using the user's blender install """

    if platform.system().lower() == 'windows':
        blender_path = WIN_BLENDER_INSTALL_PATH
    else:
        blender_path = 'blender'

    command = [ blender_path, '-b', '-P', script ] + list(args)
    try:
        subprocess.run(command)
    except FileNotFoundError:
        indent   = ' ' * 4
        reindent = lambda s: (indent + '\n').join([
            line.strip()
            for line in s.strip().split('\n')
        ])
        print(reindent("""
            Couldn't run blender: shell command "%s" failed.
            If you're a windows user, either change WIN_BLENDER_INSTALL_PATH (currently '%s')
            in run_bpy.py, or add blender to your PATH.

            If you're a mac or linux user, you likely do not have blender installed and in your path
            (would recommend installing through a package manager, like brew or apt-get)
        """)%(' '.join(command), command[0]))


def run_self ():
    if not sys.argv[0].endswith('blender'):
        print("Running self with blender: %s"%(' '.join(sys.argv)))
        run_blender_script(sys.argv[0], *sys.argv[1:])
        sys.exit()
    print("Running from within blender: %s"%(' '.join(sys.argv)))


if __name__ == '__main__':
    try:
        run_blender_script(*sys.argv[1:])
    except ValueError:
        print("Usage: %s <script>.py"%(sys.argv[0]))
