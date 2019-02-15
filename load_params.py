import sys
import os
import multiprocessing
from serialization_utils import serialize_object, deserialize_object

def load_json_files (directory, num_processes = 8, file_ext = '.json'):
    print("Scanning '%s'"%directory)
    files = [
        os.path.join(dirpath, file)
        for dirpath, subdirs, files in os.walk(directory)
        for file in files
        if file.endswith(file_ext)
    ]
    print("Found %s files"%len(files))
    print("Loading files...")

    pool = multiprocessing.Pool(num_processes)

    dataset = {}
    i = 0
    for path, data in zip(files, pool.map(deserialize_object, files)):
        dataset[path] = data
        print("%d / %d: loaded '%s'"%(i, len(files), path))
        i += 1
    return dataset

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: %s <import-path> <export-file>"%(sys.argv[0]))
    else:
        dataset = load_json_files(sys.argv[1])
        serialize_object(sys.argv[2], dataset)
