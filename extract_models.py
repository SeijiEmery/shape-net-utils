import os
import json

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
# Get shapenet ids from taxonomy.json
#

def get_matching_shapenet_model_ids (shapenet_dir, matching_keywords, non_matching_keywords=None):
    """ finds + returns matching synsetIds from matching shapenet
    taxonomy groups in <shapenet_dir>/taxonomy.json """


    matching_keywords = set(matching_keywords or [])
    non_matching_keywords = set(non_matching_keywords or [])

    taxonomy_path = os.path.join(shapenet_dir, 'taxonomy.json')
    if not os.path.exists(taxonomy_path):
        raise Exception("file '%s' does not exist!"%taxonomy_path)

    with open(taxonomy_path, 'r') as f:
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

if __name__ == '__main__':
    # extract_models()
    get_matching_shapenet_model_ids('shapenet', [ 'car' ])
    print()
    get_matching_shapenet_model_ids('shapenet', [ 'car' ], [ 'cruiser', 'minvan', 'jeep' ])
    print()
    get_matching_shapenet_model_ids('shapenet', [ 'jeep' ], [])
