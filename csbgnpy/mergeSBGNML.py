#!/bin/python

import argparse
from Utils import *

usage = "usage: %mergeSBGNML OUTPUT INPUT(s)"
parser = argparse.ArgumentParser(usage = usage)
parser.add_argument("output", help="OUTPUT FILE")
parser.add_argument("inputs", type=argparse.FileType('r'), help = "INPUT FILE", nargs='+')
args = parser.parse_args()

net = Utils.readSBGNML(*args.inputs)
Utils.writeSBGNML(net, args.output)
