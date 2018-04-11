#!/bin/env python

import argparse
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre FMC PROM data', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-d', '--device', default='M24C02', help='PROM device to target (M24C02/AT24C32D)')
parser.add_argument('-a', '--address', type=int)
parser.add_argument('-w', '--write_value', type=int)
parser.add_argument('-b', '--bottom_site', action="store_true", help='Select bottom HPC site (default is top LPC site)')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

if args.address == None:
   raise Exception('Write address not specified')

if args.write_value == None:
   raise Exception('Write value not specified')

# Most PROMs have similar basic behavior on the QF2-pre, but the exact addressing varies.
# Typically, the PROM base address is (0x50 | ADDR), where ADDR == 0 to 7 depending on how GA0 & GA1 are wired up.
# In the QF2-pre, the top FMC is GA0 = GA1 = 0, the bottom FMC is GA0 = 1, GA1 = 0.

# For the HW-FMC-105-DEBUG: TOP FMC == 0x50, BOTTOM FMC == 0x52, DEVICE == m24c02
# For the other mezzanines using the AT24C32D: TOP FMC == 0x50, BOTTOM FMC == 0x51, DEVICE == at24c32d

# To read or write a byte from a given address, use:
# write_[DEVICE]_prom(PROM ADDRESS, ADDRESS, BYTE)
# read_[DEVICE]_prom(PROM ADDRESS, ADDRESS, BYTE)

print('Device selected: '+args.device)
print('Address selected: '+str(args.address))
print('Value to write: '+str(args.write_value))
if args.device == 'M24C02':
   x.write_m24c02_prom(args.address, args.write_value, args.bottom_site)
elif args.device == 'AT24C32D':
   x.write_at24c32d_prom(args.address, args.write_value, args.bottom_site)
else:
   raise Exception('Device selected is not recognized')

