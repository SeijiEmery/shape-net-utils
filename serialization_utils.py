import os
import pickle
import json
import zipfile
from time import time

def do_file_action (path, mode, action):
    if path.endswith('.zip'):
        with zipfile.ZipFile(path, mode.strip('b')) as zfile:
            with zfile.open(path.strip('.zip'), mode.strip('b')) as f:
                return action(f)
    else:
        with open(path, mode) as f:
            # print("opening '%s' with mode '%s'"%(path, mode))
            return action(f)

def serialize_object (path, data):
    basedir, file = os.path.split(path)
    if basedir and not os.path.exists(basedir):
        os.makedirs(basedir)

    print("Saving '%s'..."%path)
    t0 = time()
    actions = {
        'json': lambda f: f.write(json.dumps(data).encode('utf-8')),
        'pkl': lambda f: pickle.dump(data, f)
    }
    mode = { 'json': 'wb', 'pkl': 'wb' }
    ext = file.split('.')[1]
    do_file_action(path, mode[ext], actions[ext])
    print("OK, saved in %s"%(time() - t0))

def deserialize_object (path):
    if not os.path.exists(path):
        raise FileNotFoundError("File does not exist: '%s'"%path)
    basedir, file = os.path.split(path)

    print("Attempting to load '%s'..."%path)
    t0 = time()
    actions = {
        'json': lambda f: json.loads(f.read().decode('utf-8')),
        'pkl': lambda f: pickle.load(f)
    }
    mode = { 'zip': 'rb', 'json': 'rb', 'pkl': 'rb' }
    ext = file.split('.')[1]
    result = do_file_action(path, mode[ext], actions[ext])
    print("OK, loaded in %s"%(time() - t0))
    return result

if __name__ == '__main__':
    data = { 'foo': 1, 'bar': [1, 2] }
    for ext in ('.json', '.pkl', '.json.zip', '.pkl.zip'):
        path = 'foo/tempdir/foo' + ext
        serialize_object(path, data)
        read_data = deserialize_object(path)
        if data != read_data:
            raise Exception("%s != %s!"%(read_data, data))

    # os.rmdir('foo/tempdir')
    print("OK")
