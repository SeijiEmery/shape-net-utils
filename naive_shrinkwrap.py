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
    argv = sys.argv[3:]
else:
    argv = sys.argv

# re-run self from within blender if bpy not available.
# lets you run this script directly, while really running it from within blender's python install.
# note: the code above is to fix imports (re-add the local working directory to the python search path)
# when this happens
from run_bpy import run_self
run_self()

# End header...
import bpy

def clear_all_objects ():
    print("deleting %s objects: %s"%(
        len(bpy.context.selected_objects),
        bpy.context.selected_objects))
    bpy.ops.object.delete()

def import_and_join_obj (path, join_into = None):
    print("%s objects selected"%(len(bpy.context.selected_objects)))
    print("importing '%s'"%path)
    result = bpy.ops.import_scene.obj(filepath=path)
    if 'FINISHED' not in result:
        raise Exception("Obj import failed: '%s'"%path)
    print("imported %s objects"%(len(bpy.context.selected_objects)))
    ctx = bpy.context.copy()
    ctx['active_object']    = join_into or bpy.context.selected_objects[0]
    ctx['selected_objects'] = bpy.context.selected_objects
    bpy.ops.object.join(ctx)
    print("joined into %s"%ctx['active_object'])
    return ctx['active_object']

def apply_shrinkwrap (src, dst, subdivisions):
    print("Creating modifiers...")
    subdiv_modifier = dst.modifiers.new(name='subdiv', type='SUBSURF')
    subdiv_modifier.levels = subdivisions
    subdiv_modifier.render_levels = subdivisions

    shrinkwrap_modifier = dst.modifiers.new(name='shrinkwrap', type='SHRINKWRAP')
    shrinkwrap_modifier.target = src

    print("Applying modifiers...")
    bpy.context.scene.objects.active = dst
    bpy.ops.object.modifier_apply(modifier='subdiv')
    bpy.ops.object.modifier_apply(modifier='shrinkwrap')
    print("Done")
    return dst

def delete_everything_but_object (obj):
    bpy.ops.object.select_all(action='SELECT')
    obj.select = False
    bpy.ops.object.delete()
    obj.select = True
    return obj

def export_obj (obj, path):
    delete_everything_but_object(obj)
    bpy.ops.export_scene.obj(filepath=path)


def execute_shrinkwrap (import_path, export_path, subdivisions):
    clear_all_objects()
    obj = import_and_join_obj(import_path)
    result = bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object

    print("Imported object = %s"%obj)                       # joined obj components
    print("Target object = %s"%cube)
    apply_shrinkwrap(src=obj, dst=cube, subdivisions=subdivisions)
    export_obj(cube, export_path)

if __name__ == '__main__':
    if len(argv) < 3:
        print("Usage: %s <import-path>.obj <export-path>.obj [<num-subdivisions>]"%(args[0]))

    DEFAULT_SUBDIVISIONS = 2
    execute_shrinkwrap(
        import_path = args[1],
        export_path = args[2],
        subdivisions = args[3] if len(args) > 2 else DEFAULT_SUBDIVISIONS
    )

    # OBJ_IMPORT_PATH = "/Users/semery/projects/shape-net-utils/car_models/ShapeNetCore.v2/02958343/371c5e74c66d22d451973ec97171fea3/models/model_normalized.obj"
    # OBJ_EXPORT_PATH = "/Users/semery/projects/shape-net-utils/shrinkwrap-exports/02958343-371c5e74c66d22d451973ec97171fea3.obj"

    # execute_shrinkwrap(OBJ_IMPORT_PATH, OBJ_EXPORT_PATH, subdivisions = 2)
