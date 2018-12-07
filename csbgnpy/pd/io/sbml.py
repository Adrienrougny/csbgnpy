import tempfile
import subprocess
import shutil
import os.path

import csbgnpy.config
import csbgnpy.pd.io.sbgnml

def read(*filenames):
    """Builds a map from SBML files using the SBFC converter

    :param filenames: names of files to be read
    :return: a map that is the union of the maps described in the input files
    """
    CONVERTER = os.path.join(csbgnpy.config.SBFC_PATH, "sbml2sbgnml.sh")
    sbgnfiles = []
    for filename in filenames:
        temp = tempfile.mkstemp(suffix = ".xml")[1]
        shutil.copy2(filename, temp)
        out = subprocess.check_output([CONVERTER, temp])
        sbgnfiles.append("{}.sbgn".format(temp[:-4]))
    net = csbgnpy.pd.io.sbgnml.read(*sbgnfiles)
    return net
