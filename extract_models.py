import os
import json
import zipfile

#
# Helper functions
# 

# Python asserts don't seem to always work, so write our own assert fcn
def assert_eq (a, b):
    """ asserts a == b """
    if a != b:
        raise Exception("Expected %s == %s"%(a, b))

# assert_eq(True, False)                # Uncomment for check
assert_eq(bool(set()), False)
assert_eq(bool(set([ 'A' ])), True)


def set_match (A, B):
    """ returns true iff sets A, B intersect / have common elements """
    return bool(A & B)

def assert_set_match (A, B, expected):
    """ asserts set_match(A, B) == expected """
    if set_match(A, B) != expected:
        raise Exception("Expected %s %s %s"%(
            A, '==' if expected else '!=', B))

# assert_set_match(set(), set(), True)  # Uncomment for sanity check
assert_set_match(set(), set(), False)
assert_set_match(set([ 'A' ]), set(), False)
assert_set_match(set(), set([ 'B' ]), False)
assert_set_match(set([ 'A' ]), set([ 'B' ]), False)
assert_set_match(set([ 'A', 'B' ]), set([ 'B' ]), True)
assert_set_match(set([ 'A' ]), set([ 'B', 'A' ]), True)
assert_set_match(set([ 'A', 'B' ]), set([ 'B', 'A' ]), True)


def keyword_list_match (keyword_string, matching_keywords, non_matching_keywords):
    """ returns true iff the keywords in keyword_string (as a comma separated string) all:
    1) are non-empty
    2) match any of the keywords in matching_keywords
    3) do not match any of the keywords in non_matching_keywords

    Either of these can be an empty set.
    If matching_keywords is empty, will match all keywords (that are not in non_matching_keywords)
    """

    keywords = set([ kw.strip() for kw in keyword_string.split(',') if kw.strip() != '' ])
    # print('kw: %s (%s)'%(keywords, not keywords))
    # print('mk: %s => %s'%(matching_keywords, matching_keywords & keywords))
    # print('nk: %s => %s'%(non_matching_keywords, non_matching_keywords & keywords))
    if not keywords:
        return False

    if set_match(keywords, non_matching_keywords):
        return False

    if not matching_keywords:
        return True

    return set_match(keywords, matching_keywords)

    return (
        keywords
        and (not set_match(keywords, non_matching_keywords))
        and (not matching_keywords or set_match(keywords, matching_keywords))
    )

def assert_keyword_list_match (keyword_string, matching_keywords, non_matching_keywords, expected):
    result = keyword_list_match(keyword_string, matching_keywords, non_matching_keywords)
    if result != expected:
        raise Exception("Expected keyword_list_match(\n\t'%s',\n\t%s,\n\t%s)\n\t== %s, got %s"%(
            keyword_string, matching_keywords, non_matching_keywords, expected, result))

# empty keywords should not match anything
assert_keyword_list_match('', set(), set(), False)           
assert_keyword_list_match('', set([ 'a' ]), set(), False)       
assert_keyword_list_match('', set(), set([ 'b' ]), False)       
assert_keyword_list_match('', set([ 'a' ]), set([ 'b' ]), False)

# empty match list should match everything (except when hitting non_matching_keywords)
assert_keyword_list_match('a,b', set(), set(), True)
assert_keyword_list_match('a,b', set(), set([ 'c' ]), True)
assert_keyword_list_match('a,b', set(), set([ 'a' ]), False)
assert_keyword_list_match('a,b', set(), set([ 'b' ]), False)
assert_keyword_list_match('a,b', set(), set([ 'a' ]), False)

# should match matching kws
assert_keyword_list_match('a,b', set([ 'a' ]), set(), True)
assert_keyword_list_match('a,b', set([ 'b' ]), set(), True)
assert_keyword_list_match('a,b', set([ 'c' ]), set(), False)
assert_keyword_list_match('a,b', set([ 'a', 'b' ]), set(), True)
assert_keyword_list_match('a,b', set([ 'a', 'b', 'c' ]), set(), True)
assert_keyword_list_match('a,b', set([ 'a', 'c', 'd' ]), set(), True)

# unless hit in non-matching
assert_keyword_list_match('a,b', set([ 'a', 'b' ]), set([ 'a' ]), False)
assert_keyword_list_match('a,b', set([ 'a', 'b' ]), set([ 'c' ]), True)

#
# Utility for reading files .zip or directory files...
#

class ShapenetArchive:
    def __init__ (self, path):
        self.path = path

    def __enter__ (self):
        return self

    def __exit__ (self, type, value, traceback):
        self.close()


class FileCache ():
    """ File cache layer for ShapenetZipArchive. Will only effectively store the .json file """

    def __init__ (self, archive, cache_dir = './.cached_files'):
        print("Loading file cache...")
        self.archive = archive
        self.cache_dir = cache_dir
        self.file_cache = {}
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    path = os.path.join(*(dirs + [ file ]))
                    cache_dir = os.path.join(root, path)
                    self.file_cache[path] = cache_dir

        for path, cache_path in self.file_cache.items():
            print("   cache '%s' => '%s'"%(path, cache_path))

    def open (self, path, *args, **kwargs):
        # If file not in cache, read it from archive and write it to file cache
        if path not in self.file_cache:
            cached_path = os.path.join(self.cache_dir, path)
            self.file_cache[path] = cached_path

            with self.archive.open(path, 'r') as input_file:

                # Make directories
                path_dirs = os.path.split(cached_path)[0]
                if not os.path.exists(path_dirs):
                    os.makedirs(path_dirs)

                # Write file
                print("Writing '%s' to cache (at '%s')"%(path, cached_path))
                data = input_file.read()
                try:
                    with open(cached_path, 'w') as f:
                        f.write(data)
                except TypeError:
                    with open(cached_path, 'wb') as f:
                        f.write(data)

        # Read cached file from disk
        return open(self.file_cache[path], *args, **kwargs)

    def close (self):
        self.archive.close()

    # Forward __enter__ / __exit__ to archive

    def __enter__ (self):
        self.archive.__enter__()
        return self

    def __exit__ (self, *args):
        self.archive.__exit__(*args)


class ShapenetZipArchive (ShapenetArchive):
    """ Encapsulates a lazily loaded ZipFile archive w/ file caching """

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive = None
        self.cache_dir = './.cached-files'

    def lazy_load (self):
        if not self.archive:
            print("Loading '%s'..."%self.path)
            self.root_path = os.path.split(self.path)[1].strip('.zip')
            self.archive   = zipfile.ZipFile(self.path, 'r')

    def open (self, path, *args, **kwargs):
        self.lazy_load()
        path = os.path.join(self.root_path, path)
        return self.archive.open(path, *args, **kwargs)

    def close (self):
        if self.archive:
            print("Closing '%s'"%self.path)
            self.archive.close()
            self.archive = None


class ShapenetDirArchive (ShapenetArchive):
    """ Encapsulates a plain unzipped directory w/ the same interface as ShapenetZipArchive """

    def open (self, path, *args, **kwargs):
        path = os.path.join(self.path, path)
        if not os.path.exists(path):
            raise Exception("File '%s' does not exist!"%path)
        return open(path, *args, **kwargs)

    def close (self):
        pass


def load_shapenet_archive (path):
    """ Loads a shapenet archive (either .zip or plain root directory), encapsulating
    the different kinds of shapenet archives that may be used (either .zip or unzipped)
    via ShapenetZipArchive and ShapenetDirArchive w/ a duck-typed interface
    """
    if path.endswith('.zip'):
        return FileCache(ShapenetZipArchive(path))
    return ShapenetDirArchive(path)

#
# Get shapenet ids from taxonomy.json
#

def get_matching_shapenet_model_ids (shapenet_archive, matching_keywords, non_matching_keywords=None):
    """ finds + returns matching synsetIds from matching shapenet
    taxonomy groups in <shapnet_zip_archive>/taxonomy.json """

    matching_keywords = set(matching_keywords or [])
    non_matching_keywords = set(non_matching_keywords or [])

    taxonomy_path = 'taxonomy.json'
    with shapenet_archive.open(taxonomy_path, 'r') as f:
        data = json.loads(f.read())

    items_by_synset = {
        item['synsetId']: item
        for item in data
    }

    matching_synsets = {}
    indent = 0

    def add_synset (synsetId):
        nonlocal indent
        indent += 1
        item = items_by_synset[synsetId]
        if synsetId not in matching_synsets and keyword_list_match(item['name'], set(), non_matching_keywords):
            matching_synsets[synsetId] = item
            for child in item['children']:
                if child in matching_synsets:
                    continue

                # print("%s => child %s => %s"%(
                #     '\t' * indent,
                #     synsetId, items_by_synset[synsetId]['name']))
                add_synset(child)

    print("Querying all models matching %s and not %s"%(
        matching_keywords or '<none>', non_matching_keywords or '<none>'))
    for item in data:
        if keyword_list_match(item['name'], matching_keywords, non_matching_keywords):
            # print("matched %s => %s"%(item['synsetId'], item['name']))
            indent = 0
            add_synset(item['synsetId'])

    for synsetId, item in matching_synsets.items():
        print('%s => %s'%(synsetId, item['name']))
    return matching_synsets.keys()
    # print(matching_synsets)

#
# Resolve into actual directory paths
#

# TBD

#
# Extract files to an external directory
#

# TBD

def extract_models (shapenet_dir, keywords, output_dir):
    pass

# TBD: add zip file support for all of the above

def print_zip_archive_contents (shapenet_zip_archive):
    for file in shapenet_zip_archive.infolist():
        print(file)


if __name__ == '__main__':
    # extract_models()

    shapenet_path = './ShapeNetCore.v2.zip'
    # shapenet_path = 'shapenet'
    with load_shapenet_archive(shapenet_path) as shapenet_archive:
        get_matching_shapenet_model_ids(shapenet_archive, [ 'car' ])
        print()
        get_matching_shapenet_model_ids(shapenet_archive, [ 'car' ], [ 'cruiser', 'minvan', 'jeep' ])
        print()
        get_matching_shapenet_model_ids(shapenet_archive, [ 'jeep' ], [])
