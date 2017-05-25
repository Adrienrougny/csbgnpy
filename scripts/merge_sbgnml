#!/bin/python

import argparse
from csbgnpy.pd.sbgnmlio import read_sbgnml
from csbgnpy.pd.sbgnmlio import write_sbgnml

usage = "usage: %merge_sbgnml OUTPUT INPUT(s)"
parser = argparse.ArgumentParser(usage = usage)
parser.add_argument("--no-renew-ids", dest = "renew_ids", action = "store_false", default = True)
parser.add_argument("output", help="OUTPUT FILE")
parser.add_argument("inputs", type=argparse.FileType('r'), help = "INPUT FILE", nargs='+')

args = parser.parse_args()

net = read_sbgnml(*args.inputs)
write_sbgnml(net, args.output, args.renew_ids)
