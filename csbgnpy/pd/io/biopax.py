import tempfile
import subprocess
import shutil
import os.path

import csbgnpy.config
import csbgnpy.pd.io.sbgnml

def read(*filenames):
    """Builds a map from Biopax files using paxtools

    :param filenames: names of files to be read
    :return: a map that is the union of the maps described in the input files
    """
    CONVERTER = os.path.join(csbgnpy.config.PAXTOOLS_PATH, "biopax2sbgnml.sh")
    sbgnfiles = []
    for filename in filenames:
        temp = tempfile.mkstemp()[1]
        out = subprocess.check_output([CONVERTER, filename, temp, "-nolayout"])
        sbgnfiles.append(temp)
    net = csbgnpy.pd.io.sbgnml.read(*sbgnfiles)
    return net
