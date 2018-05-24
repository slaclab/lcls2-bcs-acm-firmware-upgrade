#!/usr/bin/env python

import time, sys, argparse
from qf2_python.configuration.jtag import *
from qf2_python.configuration.spi import *

# Dynamic execution helper
def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Verify Spartan-6 configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Store bootloader')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for PROM interface')

args = parser.parse_args()

# Chose firmware location
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0
else:
    FIRMWARE_SECTOR_OFFSET = 32

FIRMWARE_ID_ADDRESS = (FIRMWARE_SECTOR_OFFSET+23) * spi.constants.SECTOR_SIZE
CONFIG_ADDRESS = (FIRMWARE_SECTOR_OFFSET+24) * spi.constants.SECTOR_SIZE
SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Read the VCR and VECR
#if args.verbose == True:
#    print('Scanning PROM bitstream and generating search hash')

# Use the hash of the bitstream to determine the configuration
#prom_hash = prom.read_hash(FIRMWARE_SECTOR_OFFSET * spi.constants.SECTOR_SIZE, 23 * spi.constants.SECTOR_SIZE)

# Convert the hash to text
#s = str()
#for j in prom_hash[0:32]:
#    s += '{:02x}'.format(j)
#prom_hash = s

#if args.verbose == True:
#    print('Loading configuration interface matching SHA256: '+prom_hash)

# Get the configuration object for this firmware version
#cfg = my_exec_cfg(s, True)

# Check the stored SHA256 to see what configuration space we should be using
pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)

s = str()
for i in pd[0:32]:
    s += '{:02x}'.format(i)
print('Stored SHA256:'+s)

print('Selecting matching configuration interface...')

cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+s+' as x', args.verbose)

# TODO - Warn on mismatch with running firmware
#x = qf2_python.identifier.get_board_information(args.target, args.verbose)

print('Importing stored Spartan-6 configuration settings...')

if ( cfg.import_prom_data(prom.read_data(CONFIG_ADDRESS, 256)) == False ):
    exit(1)

print('')
print('Network configuration is currently:')
print('')

cfg.print_network_cfg()

print('')
print('Firmware configuration is currently:')
print('')

cfg.print_write_cfg()
