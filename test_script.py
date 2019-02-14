try:
    from run_bpy import run_self
    run_self()
except ImportError:
    import bpy
    import sys

print("Hello, world!")
print("Commandline args: %s"%sys.argv)
