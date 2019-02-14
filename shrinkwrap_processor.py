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
from naive_shrinkwrap import execute_shrinkwrap
import json
import multiprocessing

def run_shrinkwrap_worker (task_bundle):
    print("STARTING WORKER %s (%s tasks)"%(
        task_bundle['worker'], len(task_bundle['tasks'])))
    for i, task in enumerate(task_bundle['tasks']):
        if os.path.exists(task['export']):
            print("Skipping %s, already exists"%task['export'])

        print("Running worker %s, task %s: %s => %s"%(
            task_bundle['worker'], i, task['import'], task['export']
        ))

        path = os.path.split(task['export'])[0]
        if not os.path.exists(path):
            os.makedirs(path)
        execute_shrinkwrap(task['import'], task['export'], task_bundle['subdivisions'])

def generate_shapenet_tasks (shapenet_synsets_dir, output_dir):
    for synset_dir in os.listdir(shapenet_synsets_dir):
        synset_dir_path = os.path.join(shapenet_synsets_dir, synset_dir)
        for model_dir in os.listdir(synset_dir_path):
            model_dir_path = os.path.join(synset_dir_path, model_dir)
            obj_files = [
                os.path.join(dir, file) 
                for dir, subdirs, files in os.walk(model_dir_path)
                for file in files
                if file.endswith('.obj')
            ]
            if len(obj_files) != 1:
                print("Directory '%s' has an incorrect # of .obj files: %s"%(
                    model_dir_path, obj_files))
            else:
                obj_file = obj_files[0]
                yield {
                    'import': os.path.abspath(obj_file),
                    'export': os.path.abspath(os.path.join(output_dir, '%s-%s.obj'%(
                        synset_dir, model_dir)))
                }

def save_shrinkwrap_tasks (task_json_file, tasks):
    with open(task_json_file, 'w') as f:
        f.write(json.dumps(tasks))

def load_shrinkwrap_tasks (task_json_file):
    with open(task_json_file, 'r') as f:
        return json.loads(f.read())

def run_shrinkwrap_tasks (shapenet_synsets_dir, output_dir, subdivisions, num_workers, use_cached_tasks = False):
    task_file = 'tasks-%s-%s.json'%(subdivisions, num_workers)
    if use_cached_tasks and os.path.exists(task_file):
        tasks = load_shrinkwrap_tasks(task_file)
    else:
        task_bundles = [ list() for i in range(num_workers) ]
        task_items = list(generate_shapenet_tasks(shapenet_synsets_dir, output_dir))
        for i, task in enumerate(task_items):
            task_bundles[ i % num_workers ].append(task)

        print("Total # tasks: %s"%len(task_items))
        for i, bundle in enumerate(task_bundles):
            print("%s: %s tasks"%(i, len(bundle)))

        tasks = {
            'num_tasks': len(task_items),
            'subdivisions': subdivisions,
            'num_workers': num_workers,
            'task_bundles': [
                { 'worker': i, 'tasks': task_bundles[i], 'subdivisions': subdivisions }
                for i in range(num_workers)
            ]
        }
        save_shrinkwrap_tasks(task_file, tasks)

    print("Running %s tasks on %s workers"%(
        tasks['num_tasks'], tasks['num_workers']
    ))
    if num_workers > 1:
        pool = multiprocessing.Pool(num_workers)
        pool.map(run_shrinkwrap_worker, tasks['task_bundles'])
        # map(run_shrinkwrap_worker, tasks['task_bundles'])
    else:
        run_shrinkwrap_worker(tasks['task_bundles'][0])

if __name__ == '__main__':
    SUBDIVISION_LEVELS = 2
    NUM_WORKERS = 4

    run_shrinkwrap_tasks(
        './car_models/ShapeNetCore.v2',
        'shrinkwrap-exports',
        SUBDIVISION_LEVELS,
        NUM_WORKERS,
        # use_cached_tasks = True
    )
