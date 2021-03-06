import os
import sys
from serialization_utils import serialize_object, deserialize_object


def parse_obj_line (line, data, 
        check_verts_normalized = True,
        expect_verts_normalized = True, 
        check_normals_normalized = True,
        expect_normals_normalized = True, 
        check_face_index_bounds = True,
        expect_face_count = None,
        expect_consistent_face_count = True,
        **kwargs):

    if line.startswith('v '):
        x, y, z = map(float, line[2:].strip().split())
        if check_verts_normalized:
            normalized = x * x + y * y + z * z <= 1.0
            if not normalized:
                data['verts_normalized'] = False
                if expect_verts_normalized:
                    raise Exception("vertex not normalized!")

        data['verts'] += [ (x, y, z) ]

    elif line.startswith('vn '):
        x, y, z = map(float, line[3:].strip().split())
        if check_normals_normalized:
            normalized = x * x + y * y + z * z == 1.0
            if not normalized:
                data['normals_normalized'] = False
                if expect_normals_normalized:
                    raise Exception("vertex normal not normalized!")

        data['normals'] += [ (x, y, z) ]

    elif line.startswith('f '):
        # if '/' in line:
        #     indices = list(map(int, line[2:].strip().split('/')))
        # else:
        indices = [
            int(indices.split('/')[0])
            for indices in line[2:].strip().split()
        ]

        if check_face_index_bounds:
            data['min_face_index'] = min(data['min_face_index'], *indices)
            data['max_face_index'] = max(data['max_face_index'], *indices)

        if expect_face_count and len(indices) != expect_face_count:
            raise Exception("Invalid face count: %s indices, expected %s!"%(
                len(indices), expect_face_count))

        elif expect_consistent_face_count and len(indices) != data['face_count']:
            if data['face_count'] is None:
                data['face_count'] = len(indices)
            else:
                raise Exception("Mismatched face count: %s, prev %s"%(
                    len(indices), data['face_count']))

        data['faces'] += indices


def read_obj (path, check_face_index_bounds = True, **kwargs):
    """ Reads the vertex, vertex normal, and face components of an .obj file.

    Returns data, errors where
        errors:             list or None
        data['verts']:      flat list of verts          (float x, y, z)
        data['normals']:    flat list of vert normals   (float x, y, z)
        data['faces']:      flat list of face indices. May be negative.
        data['face_count']: num elements per face. expected to be 3 (tris) or 4 (quads)
        data['verts_normalized']:   True iff vertex elements are all in [0, 1]
        data['normals_normalized']: True iff normals all have length 1

    See parse_obj_line for full kwargs.

    Usage:
        path = "path/to/some_obj.obj"
        data, errors = read_obj(path, kwargs...)
        if errors:
            raise Exception("Failed to read '%s' (%d errors):\n\t"%(
                path, len(errors), '\n\t'.join(errors)))
    """

    data = {
        'min_face_index': 0, 'max_face_index': 0, 'face_count': None,
        'verts_normalized': True, 'normals_normalized': True,
        'verts': [],
        'normals': [],
        'faces': []
    }

    errors = []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            try:
                parse_obj_line(line, data, check_face_index_bounds=check_face_index_bounds, **kwargs)
            except Exception as e:
                errors.append("error at %s:%d '%s':\n\t%s"%(
                    path, i, line.strip(), e))

    # Check consistency...
    if check_face_index_bounds:
        if data['min_face_index'] < 0 and abs(data['min_face_index']) >= len(data['verts']) * 3:
            errors.append("min face index %s out of bounds! (%s verts)"%(
                data['min_face_index'], len(data['verts'])))

        if data['max_face_index'] >= len(data['verts']) * 3:
            errors.append("max face index %s out of bounds! (%s verts)"%(
                data['max_face_index'], len(data['verts'])))

    return data, (errors or None)


def objs_have_same_topology (obj1data, obj2data):
    # print(obj1data, obj2data)
    return obj1data['faces'] == obj2data['faces']

def obj_is_normalized (objdata):
    return objdata['verts_normalized']

def validate_data_samples (*objpaths, **kwargs):
    objdata = []

    normals_valid, topology_valid = True, True
    for path in objpaths:
        print("Loading '%s'"%path)
        obj, errors = read_obj(path, expect_verts_normalized = False, **kwargs)
        if errors:
            raise Exception("Failed to read '%s' (%d errors):\n\t%s"%(
                path, len(errors), '\n\t'.join(errors)))
        if not obj_is_normalized(obj):
            normals_valid = False
            print("'%s' does not have normalized vertices!"%path)
        objdata.append((obj, path))

    obj1, obj1path = objdata[0]
    for obj2, obj2path in objdata[1:]:
        if not objs_have_same_topology(obj1, obj2):
            topology_valid = False
            print("'%s', '%s' have different topology"%(obj1path, obj2path))

    print("Validation %s"%("successful" if normals_valid and topology_valid else "failed"))
    print("\thave matching topology: %s"%topology_valid)
    print("\tvertices are normalized: %s"%normals_valid)

def obj_extract_params (objdata):
    corners = objdata['verts'][:8]
    print("Corners:")
    sign = [ '-', '+' ]
    for i, verts in enumerate(corners):
        print("%sx %sy %sz: %s"%(
            sign[i & 1], sign[(i >> 1) & 1], sign[(i >> 2) & 1],
            verts
        ))
    print("%s remaining vertices"%(len(objdata['verts'][8:])))

    # plane_verts = [
    #     (dir, [ corner for i, corner in enumerate(corners)
    #         if ((i >> (k // 2)) & 1) == (k & 1) 
    #     ])
    #     for k, dir in enumerate((
    #         (-1.0, 0.0, 0.0),
    #         (+1.0, 0.0, 0.0),
    #         (0.0, -1.0, 0.0),
    #         (0.0, +1.0, 0.0),
    #         (0.0, 0.0, -1.0),
    #         (0.0, 0.0, +1.0),
    #     ))
    # ]

    # def subv (a, b):
    #     return tuple([ a - b for a, b in zip(a, b) ])

    # def mulv (a, s):
    #     return tuple([ a * s for a in a ])

    # def addv (a, b):
    #     return tuple([ a + b for a, b in zip(a, b) ])

    # for i, (dir, verts) in enumerate(plane_verts):
    #     print("plane %s: %s"%(i, dir))
    #     print("\t%s"%"\n\t".join(map(str, verts)))
    #     print("plane direction vectors:")
    #     for i, a in enumerate(verts):
    #         for j, b in enumerate(verts):
    #             if j >= i:
    #                 break
    #             print("\t%s, %s => %s"%(i, j, subv(a, b)))

    #     u, u0 = subv(verts[1], verts[0]), verts[0]
    #     v, v0 = subv(verts[2], verts[0]), verts[0]
    #     print("\tlet u = %s * i + %s"%(u, u0))
    #     print("\tlet v = %s * j + %s"%(v, v0))
    #     for i in [ 1.0, 0.0 ]:
    #         for j in [ 1.0, 0.0 ]:
    #             print("\t\t=> %s, %s = %s"%(
    #                 i, j, addv(u0, addv(
    #                     mulv(u, i),
    #                     mulv(v, j)
    #                 ))))

    def flatten (array):
        output = []
        for elem in array:
            output += list(elem)
        return output

    return flatten(objdata['verts'])

def locate_obj_files_in_directory (path):
    return [
        os.path.join(dir, file)
        for dir, subdirs, files in os.walk(path)
        for file in files
        if file.endswith('.obj')
    ]

def extract_params (
        directory = None,
        files = None,
        export_path = None,
        **kwargs):

    objpaths = files or []
    if directory:
        objpaths += locate_obj_files_in_directory(directory)
    objpaths = set(objpaths)

    if not objpaths:
        raise Exception("No input files! (objdir = %s, objpaths = %s)"%(directory, files))

    if export_path is None:
        raise Exception("Missing export path!")

    if not os.path.exists(export_path):
        os.makedirs(export_path)

    for i, path in enumerate(objpaths):
        print("Loading '%s'"%path)
        objdata, errors = read_obj(path, expect_verts_normalized=False, **kwargs)
        if errors:
            print("Failed to load '%s' (%d errors):\n\t%s"%(
                path, len(errors), '\n\t'.join(errors)))
        else:
            data = obj_extract_params(objdata)
            filename = os.path.split(path)[1].split('.')[0]
            output_path = os.path.join(export_path, filename + '.json')
            # output_path = os.path.join(export_path, filename + '.pkl')
            serialize_object(output_path, data)
            print("Done: %d / %d"%(i + 1, len(objpaths)))

if __name__ == '__main__':
    # validate_data_samples(
    # extract_params(
    #     # directory='/Users/semery/Downloads/cubeheightobj',
    #     files = [
    #         '/Users/semery/Downloads/cubeheightobj/b17d638e7def9adbc8a6c4a50ada6f9f.obj',
    #         '/Users/semery/Downloads/cubeheightobj/b1c6a021c1c47884c9463ecce7643e8e.obj',
    #         '/Users/semery/Downloads/cubeheightobj/ff564f7ec327ed83391a2a133df993ee.obj',
    #     ],
    #     export_path='./data_params'
    # )
    # extract_params(
    #     directory='shrinkwrap-exports',
    #     export_path='shrinkwrap-export-params',
    #     check_normals_normalized=False,
    # )

    if len(sys.argv) < 3:
        print("Usage: %s <directory-containing-obj-files> <export-path>"%sys.argv[0])
    else:
        extract_params(
            directory = sys.argv[1],
            export_path = sys.argv[2],
            check_normals_normalized = False
        )
