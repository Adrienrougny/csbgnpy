import tempfile
import subprocess
import shutil
import os.path

import csbgnpy.config
import csbgnpy.pd.io.sbgnml

def read(*filenames):
    """Builds a map from CellDesigner files using the cd2sbgnml converter

    :param filenames: names of files to be read
    :return: a map that is the union of the maps described in the input files
    """
    print('aaa')
    CONVERTER = os.path.join(csbgnpy.config.CD2SBGNML_PATH, "cd2sbgnml.sh")
    sbgnfiles = []
    for filename in filenames:
        temp = tempfile.mkstemp()[1]
        out = subprocess.check_output([CONVERTER, filename, temp])
        sbgnfiles.append(temp)
    net = csbgnpy.pd.io.sbgnml.read(*sbgnfiles)
    return net
