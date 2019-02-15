
## To shrinkwrap an obj file:

Run

    python3 naive_shrinkwrap.py <path/to/an/obj/file.obj> <path/to/obj/export.obj>

To run with n subdivision levels:

    python3 naive_shrinkwrap.py <path/to/an/obj/file.obj> <path/to/obj/export.obj> <n>


## To mass-run shrinkwrap on a shapenet directory

    python3 shrinkwrap_processor.py <path/to/a/shapenet/dir> [<export-path>] [<num-processes>] [<subdivision-levels>]
    
The shapenet directory path must contain a set of subdirectories (synsets) with names like `02747177`, which should each contain model directories (eg. `95ddaba8142bb8572b12ea83455b0f44`).

This script will process ALL synsets / models found, so to extract specific models, either move or copy the synset directories you're interested in, and/or the models therein.

Here is a list of all the ShapeNet v2 car synsets (by tag):

    Querying all models matching {'car'} and not <none>
    02958343 => car,auto,automobile,machine,motorcar
    02701002 => ambulance
    02814533 => beach wagon,station wagon,wagon,estate car,beach waggon,station waggon,waggon
    02930766 => cab,hack,taxi,taxicab
    03100240 => convertible
    03119396 => coupe
    03141065 => cruiser,police cruiser,patrol car,police car,prowl car,squad car
    03881534 => panda car
    03498781 => hatchback
    03543394 => hot rod,hot-rod
    03594945 => jeep,landrover
    03670208 => limousine,limo
    03770679 => minivan
    03870105 => pace car
    04037443 => racer,race car,racing car
    04322801 => stock car
    04097373 => roadster,runabout,two-seater
    04166281 => sedan,saloon
    04285008 => sports car,sport car
    04285965 => sport utility,sport utility vehicle,S.U.V.,SUV
    04459122 => touring car,phaeton,tourer

(which was extracted from the taxonomy.json file by extract_models.py)

## To get raw parameter data out of the obj files (atm just vertices), run

    python3 read_obj.py <directory-containing-obj-files> <export-path> [<file-ext>]

This writes out a bunch of json files to export-path (flat array of vertices). To load this in python:
    
    directory = <export-path>
    data = {}
    for file in os.listdir(directory):
        if file.endswith('.json'):
            with open(os.path.join(directory, file), 'r') as f:
                data[file] = json.loads(f.read())
    dataset_values = np.array(data.values())
    dataset_names  = list(data.keys())


# To build out and extract a dataset:

## From the nobuyuki dataset: http://nobuyuki-umetani.com (exploring generative 3d shapes using autoencoder networks)

    python3 read_obj.py path/to/cubeheightobj nobuyuki-export json

    do stuff with the json files...

## From the shapenet dataset (note: this will take a while...)

    copy synsets / models you want to process to some directory.
        eg. copy ShapeNetCore.v2/03770679 to shapenet-minivan/03770679

    then run the following:

    python3 shrinkwrap_processor.py path/to/shapenet-minivan path/to/minivan-shrinkwrapped

    python3 read_obj.py path/to/minivan-shrinkwrapped path/to/minivan-params

    do stuff with the json files...

Note: shrinkwrap_processor may do weird things b/c apparently blender + multiprocessing weren't, uh... intended to work together. They -seem- to work together w/out errors, but, uh, if you have issues that wouldn't be surprising. Also, note that multiprocessing will spawn zombie python processes if you just try to kill the main process (ie. killing the main process won't kill the other running processes). You can 'fix' this by running `pkill python` (on \*nix), or equivalent on windows. To bypass this problem altogether, set the # of processes to 1, ie

    python3 shrinkwrap_processor.py path/to/shapenet-minivan path/to/minivan-shrinkwrapped 1

To also set the # of subdivision levels, run

    python3 shrinkwrap_processor.py path/to/shapenet-minivan path/to/minivan-shrinkwrapped 1 <# subdivision levels (defaults to 2)>

### Blender gotchas:

#### Windows:

You have to a) install blender, b) edit run_bpy.py, setting WIN_BLENDER_INSTALL_PATH to whatever path blender is located at. Or add the path to your blender executable to your path. Yes, this is a hack. Yes, we're doing some really disgusting things to run blender / bpy b/c `pip install bpy` doesn't seem to reliably work on all platforms (and involves basically installing a copy of blender as a python module)

#### \*nix / osx:

You must install blender through a package manager, or add the path to your installed blender executable to your path. You're good if you can run `blender` from a shell.


Note: in both cases, you should get a helpful error message that explains how to do these things if you haven't set this up yet; these instructions are just here for redundancy.
