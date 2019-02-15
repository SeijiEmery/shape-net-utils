import sys
import os
import time
from datetime import datetime

def list_files (directory, file_ext = None, pred = None):
    if file_ext and not pred:
        pred = lambda file: file.endswith(file_ext)
    
    return [
        os.path.join(dirpath, file)
        for dirpath, subdirs, files in os.walk(directory)
        for file in files
        if pred and pred(file)
    ]

def show_file_conversion_status (import_dir, export_dir, import_pred, export_pred):
    num_imports = len(list_files(import_dir, pred=import_pred))
    num_exports = len(list_files(export_dir, pred=export_pred))
    print("%s: %s / %s"%(datetime.now(), num_exports, num_imports))

def run_periodic (dt, f, *args, **kwargs):
    while True:
        f(*args, **kwargs)
        time.sleep(dt)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: %s <obj-imports> <obj-exports>"%sys.argv[0])
    else:
        is_obj = lambda file: file.endswith('.obj')
        run_periodic(1.0, lambda:
            show_file_conversion_status(sys.argv[1], sys.argv[2], is_obj, is_obj))
