#!/bin/env python

import argparse, time, datetime
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre monitors', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')

args = parser.parse_args()

x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

# Turn on Kintex
x.set_byte(0, 0x20, 0x20)

# Clear latch
x.set_byte(0, 0x10, 0x10)
x.set_byte(0, 0x00, 0x10)

while True:
    print
    x.import_network_data()
    a = x.get_read_value('DEBUG_RX_10B_DATA')
    b = x.get_read_value('DEBUG_RX_HS')
    c = x.get_read_value('LATCHED_DEBUG_RX_10B_DATA')
    d = x.get_read_value('LATCHED_DEBUG_RX_HS')
    print(hex(a))
    print(hex(b))
    print(hex(c))
    print(hex(d))
    if (b != 7) and (d != 7):
        print(b)
        print(d)
        break

