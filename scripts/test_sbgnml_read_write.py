#!/bin/python

import os
import argparse
from csbgnpy.pd.sbgnmlio import read_sbgnml
from csbgnpy.pd.sbgnmlio import write_sbgnml

usage = "usage: %test_sbgnml_read_write INPUT"
parser = argparse.ArgumentParser(usage = usage)
parser.add_argument("--no-renew-ids", dest = "renew_ids", action = "store_false", default = True)
parser.add_argument("input", help="INPUT FILE")

args = parser.parse_args()

net1 = read_sbgnml(args.input)
tempfile = "/tmp/qwertyui.sbgn"
write_sbgnml(net1, tempfile, args.renew_ids)
net2 = read_sbgnml(tempfile)
print(net1 == net2)
