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

x.import_network_data()

print(hex(x.get_read_value('DEBUG_RX_HS')))
print(hex(x.get_read_value('DEBUG_RX_10B_DATA')))
print(x.get_read_value('DEBUG_RX_DELAY_LAST_START'))
print(x.get_read_value('DEBUG_RX_DELAY_LAST_END'))
print(x.get_read_value('DEBUG_RX_DELAY_START'))
print(x.get_read_value('DEBUG_RX_DELAY_END'))
print('{:032b}'.format(x.get_read_value('DEBUG_RX_SCAN_BITS')))
print(x.get_read_value('DEBUG_RX_DELAY'))
