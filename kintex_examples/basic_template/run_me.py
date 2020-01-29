#!/bin/env python

import time, argparse, kintex_interface

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')
args = parser.parse_args()

# Get an interface
x = kintex_interface.interface(args.target)

x.setTopLED(red=1, green=0, blue=0)
time.sleep(1)
x.setTopLED(red=0, green=1, blue=0)
time.sleep(1)
x.setTopLED(red=0, green=0, blue=1)
time.sleep(1)
x.setBottomLED(red=1, green=0, blue=0)
time.sleep(1)
x.setBottomLED(red=0, green=1, blue=0)
time.sleep(1)
x.setBottomLED(red=0, green=0, blue=1)
