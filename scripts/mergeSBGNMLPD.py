#!/bin/python

import argparse
import csbgnpy.pd

usage = "usage: %mergeSBGNMLPD OUTPUT INPUT(s)"
parser = argparse.ArgumentParser(usage = usage)
parser.add_argument("--no-renew-ids", dest = "renew_ids", action = "store_false", default = True)
parser.add_argument("output", help="OUTPUT FILE")
parser.add_argument("inputs", type=argparse.FileType('r'), help = "INPUT FILE", nargs='+')

args = parser.parse_args()

net = csbgnpy.pd.utils.read_SBGNML(*args.inputs)
csbgnpy.pd.utils.write_SBGNML(net, args.output, args.renew_ids)
