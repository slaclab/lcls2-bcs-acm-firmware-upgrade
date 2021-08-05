#!/usr/bin/env python

import argparse

import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_const

parser = argparse.ArgumentParser(description='Lock Spartan-6 image and configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-r', '--region', type=int, required=True, help='Region of PROM to lock')
parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

# Check region argument
if args.region == 0:
    print('Setting PROM lock to: network configuration and Spartan bootloader')
elif args.region == 1:
    print('Setting PROM lock to: network configuration, Spartan bootloader and Spartan runtime')
elif args.region == 2:
    print('Setting PROM lock to: network configuration, Spartan bootloader, Spartan runtime and Kintex')
elif args.region == 3:
    print('Setting PROM lock to: whole PROM')
else:
    raise Exception('Lock region argument \''+str(args.region)+'\' is not a valid choice')

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=int(args.port), input_select=0, speed=0, noinit=True), args.verbose)

# Sector options
# Lock bootloader 0-31
# Lock bootloader & runtime 0-63
# Lock Kintex & Spartan reserved space 0-255
# Lock whole prom 0-511

# 1/16th, 1/8th, 1/2, 1
if args.region == 0:
    prom.lock(spi_const.LOCK_REGION_BOOTLOADER)
elif args.region == 1:
    prom.lock(spi_const.LOCK_REGION_BOOTLOADER_RUNTIME)    
elif args.region == 2:
    prom.lock(spi_const.LOCK_REGION_SPARTAN_KINTEX)    
elif args.region == 3:
    prom.lock(spi_const.LOCK_REGION_ALL)    
    
del prom
