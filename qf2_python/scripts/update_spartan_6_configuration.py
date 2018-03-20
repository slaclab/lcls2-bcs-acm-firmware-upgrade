#!/usr/bin/env python

import time, sys, argparse
import qf2_python.identifier
from qf2_python.configuration.jtag import *
from qf2_python.configuration.spi import *

def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Store Spartan-6 configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-l', '--lock', action="store_true", default=False, help='Lock bootloader')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Store bootloader')
parser.add_argument('-r', '--reboot', action="store_true", default=False, help='Reboot automatically')
parser.add_argument('-f', '--file', help='JSON settings file')
parser.add_argument('-s', '--settings', nargs='+', action='append', type=lambda kv: kv.split("="), dest='settings')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for PROM interface')

args = parser.parse_args()


# Check that the lock is only applied to the bootloader
if args.lock == True:
    if args.bootloader == False:
        print 'ERROR: Lock argument can only be used for the bootloader'
        exit(1)

# Currently disabled
#if args.reboot == True:
#    print 'ERROR: This feature is not yet supported'
#    exit(1)
if args.lock == True:
    print 'ERROR: This feature is not yet supported'
    exit(1)

# Chose firmware location
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0
else:
    FIRMWARE_SECTOR_OFFSET = 32

FIRMWARE_ID_ADDRESS = (FIRMWARE_SECTOR_OFFSET+23) * spi.SECTOR_SIZE
CONFIG_ADDRESS = (FIRMWARE_SECTOR_OFFSET+24) * spi.SECTOR_SIZE
SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Check the stored SHA256 to see what configuration space we should be using
pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)

print 'Stored SHA256:',
s = str()
for i in pd[0:32]:
    s += '{:02x}'.format(i)
print s

print 'Selecting matching configuration interface...'

cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+s+' as x', args.verbose)

# TODO - Warn on mismatch with running firmware
#x = qf2_python.identifier.get_board_information(args.target, args.verbose)

print 'Importing stored Spartan-6 configuration settings...'

pd = prom.read_data(CONFIG_ADDRESS, 256)
cfg.import_prom_data(pd)

print 'Modifying settings...'

for i in args.settings[0]:
    print(i[0]+' : '+i[1])
    unknown_key = True
    if cfg.is_network_key(i[0]):
        unknown_key = False
        cfg.set_network_key(i[0], i[1])
    if cfg.is_write_key(i[0]):
        unknown_key = False
        cfg.set_write_key(i[0], i[1])
    if unknown_key == True:
        raise Exception('Unknown key '+i[0])
print 'Exporting PROM settings...'

x = cfg.export_prom_data()

if ( x == pd ):
    print 'Values already programmed'
    # Disconnect the PROM interface before doing a reboot
    del prom
    if args.reboot == True:
        if args.bootloader == True:
            print('Rebooting with new bootloader settings')
            qf2_python.identifier.reboot_to_bootloader(args.target, args.verbose)
        else:
            print('Rebooting with new runtime settings')
            qf2_python.identifier.reboot_to_runtime(args.target, args.verbose)
    exit()

print 'Updating PROM settings...'

prom.sector_erase(CONFIG_ADDRESS)
prom.page_program(x, CONFIG_ADDRESS)

pd = prom.read_data(CONFIG_ADDRESS, 256)

if ( x != pd ):
    print 'Update failed'

# Disconnect the PROM interface before doing a reboot
del prom
if args.reboot == True:
    if args.bootloader == True:
        print('Rebooting with new bootloader settings')
        qf2_python.identifier.reboot_to_bootloader(args.target, args.verbose)
    else:
        print('Rebooting with new runtime settings')
        qf2_python.identifier.reboot_to_runtime(args.target, args.verbose)
