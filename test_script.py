#!/usr/bin/env python3

# bpy-run-from-blender fix.
# Assumes that commandline arguments are
#   sys.argv[0] = path-to-blender
#   sys.argv[1] = '-b'
#   sys.argv[2] = '-P'
#   sys.argv[3] = path-to-this-script
import sys
import os
if sys.argv[0].split('.exe')[0].endswith('blender') and sys.argv[1] == '-b' and sys.argv[2] == '-P':
    origin_script_working_directory = os.path.split(sys.argv[3])[0]
    print("setting working directory for imports: '%s'"%origin_script_working_directory)
    sys.path.insert(0, origin_script_working_directory)

# re-run self from within blender if bpy not available.
# lets you run this script directly, while really running it from within blender's python install.
# note: the code above is to fix imports (re-add the local working directory to the python search path)
# when this happens
from run_bpy import run_self
run_self()

# End header...
import bpy

print("Hello, world!")
print("Commandline args: %s"%sys.argv)
