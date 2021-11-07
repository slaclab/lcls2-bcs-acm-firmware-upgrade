#!/usr/bin/env python

import argparse

#import qf2_python.scripts.helpers as helpers
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

# Dynamic execution helper
def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Verify firmware and network configuration stored in PROM', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')

args = parser.parse_args()

identifier.verifyInBootloader(args.target, args.verbose)

NETWORK_CONFIG_ADDRESS = 24 * spi_constants.SECTOR_SIZE
BOOTLOADER_FIRMWARE_ID_ADDRESS = 23 * spi_constants.SECTOR_SIZE
BOOTLOADER_FIRMWARE_CONFIG_ADDRESS = 25 * spi_constants.SECTOR_SIZE
RUNTIME_FIRMWARE_ID_ADDRESS = (23+32) * spi_constants.SECTOR_SIZE
RUNTIME_FIRMWARE_CONFIG_ADDRESS = (24+32) * spi_constants.SECTOR_SIZE

# Fixed in current hardware
SEQUENCER_PORT = 50003

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

print('-----------------------------------------')
print('Bootloader')

# Check the stored SHA256 to see what configuration space we should be using
pd = prom.read_data(BOOTLOADER_FIRMWARE_ID_ADDRESS, 32)

b = str()
for i in pd[0:32]:
    b += '{:02x}'.format(i)
print('Stored bootloader SHA256: '+b)

print('Selecting matching configuration interface...')

cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+b+' as x', args.verbose)

# TODO - Warn on mismatch with running firmware
#x = qf2_python.identifier.get_board_information(args.target, args.verbose)

print('')
print('Importing stored Spartan-6 bootloader network configuration settings...')

if ( cfg.import_network_prom_data(prom.read_data(NETWORK_CONFIG_ADDRESS, 256)) == False ):
    exit(1)

print('')
print('Network configuration is currently:')
print('')

cfg.print_network_cfg()

print('')
print('Importing stored Spartan-6 bootloader configuration settings...')

if ( cfg.import_firmware_prom_data(prom.read_data(BOOTLOADER_FIRMWARE_CONFIG_ADDRESS, 256)) == False ):
    exit(1)
    
print('')
print('Bootloader configuration is currently:')
print('')

cfg.print_write_cfg()

print('')
print('-----------------------------------------')
print('Runtime')

pd = prom.read_data(RUNTIME_FIRMWARE_ID_ADDRESS, 32)

r = str()
for i in pd[0:32]:
    r += '{:02x}'.format(i)
print('Stored runtime SHA256: '+r)

print('Selecting matching configuration interface...')

cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+r+' as x', args.verbose)

# TODO - Warn on mismatch with running firmware
#x = qf2_python.identifier.get_board_information(args.target, args.verbose)

print('')
print('Importing stored Spartan-6 runtime network configuration settings...')

if ( cfg.import_network_prom_data(prom.read_data(NETWORK_CONFIG_ADDRESS, 256)) == False ):
    exit(1)

print('')
print('Network configuration is currently:')
print('')

cfg.print_network_cfg()

print('')
print('Importing stored Spartan-6 runtime configuration settings...')

if ( cfg.import_firmware_prom_data(prom.read_data(RUNTIME_FIRMWARE_CONFIG_ADDRESS, 256)) == False ):
    exit(1)

print('')
print('Runtime configuration is currently:')
print('')

cfg.print_write_cfg()


