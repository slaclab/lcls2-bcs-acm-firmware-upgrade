#!/usr/bin/env python

import helpers, time, sys, argparse, hashlib, qf2_python.identifier
from datetime import datetime, timedelta
from qf2_python.configuration.jtag import *
from qf2_python.configuration.spi import *

def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Store Spartan-6 image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', help='Firmware bitfile to store')
parser.add_argument('-n', '--nomigrate', action="store_true", default=False, help='Don\'t migrate configuration when updating firmware')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Store bootloader')
parser.add_argument('-r', '--reboot', action="store_true", default=False, help='Reboot automatically')
parser.add_argument('-f', '--force', action="store_true", default=False, help='Force update even if previous PROM data is unrecognized or corrupt')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

if args.bit == None:
    if args.bootloader == True:
        args.bit = 'firmwares/spartan_bootloader.bit'
    else:
        args.bit = 'firmwares/spartan_runtime.bit'
    print('Bitfile argument was not provided, assuming default from firmwares directory ('+args.bit+')')

# Sector offset is +32 for runtime image
FIRMWARE_SECTOR_OFFSET = 32

# Chose firmware location
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0

FIRMWARE_ID_ADDRESS = (FIRMWARE_SECTOR_OFFSET+23) * spi.constants.SECTOR_SIZE

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=int(args.port), input_select=0, speed=0, noinit=True), args.verbose)

# Do integrity check and check current firmware hash
prev_hash = helpers.prom_integrity_check(prom, FIRMWARE_SECTOR_OFFSET, args.verbose)

if (prev_hash == 0) and (args.force == False):
    print('ERROR: Current PROM data failed integrity check. You must use \'--force\' to continue - will set PROM settings to defaults.')
    exit(1)

if args.verbose == True:
    print('Loading bitfile: '+args.bit)

bitfile = xilinx_bitfile_parser.bitfile(args.bit)

if args.verbose == True:
    print('Design name: '+bitfile.design_name())
    print('Device name: '+bitfile.device_name())
    print('Build date: '+bitfile.build_date())
    print('Build time: '+bitfile.build_time())
    print('Length: '+str(bitfile.length()))

# Safety check to match bitfile to Spartan-6
if bitfile.device_name() != '6slx45tcsg324':
    print('ERROR: Bitfile device name is not a Spartan-6 FPGA')
    exit(1)

if bitfile.padded_hash() == prev_hash:
    print('Bitfile hash is already stored in PROM and hash is valid. Comparing PROM data for exact match...')
    if ( helpers.prom_compare_check(prom, FIRMWARE_SECTOR_OFFSET, args.bit, args.verbose) != 0 ):
        exit(0)
    print('Mismatch in PROM data - continuing')

print('Programming image')
prom.program_bitfile(args.bit, FIRMWARE_SECTOR_OFFSET)

# Generate a firwmare ID block
fw_id_data = helpers.generate_fw_id_data(args.bit)

print('Erasing old firmware ID block')
prom.sector_erase(FIRMWARE_ID_ADDRESS)

print('Updating firmware ID block')
for i in range(0, len(fw_id_data) / 256):
    prom.page_program(fw_id_data[i * 256 : (i+1) * 256], i * 256 + FIRMWARE_ID_ADDRESS, True)

s = str()
for j in fw_id_data[0:32]:
    s += '{:02x}'.format(j)
print('SHA256: '+s)

build_date = 0
for i in range(0, 8):
    build_date += int(fw_id_data[32+i]) * 2**(56-i*8)
print('Build timestamp: '+str(build_date)+' ('+str(datetime.utcfromtimestamp(build_date))+')')

storage_date = 0
for i in range(0, 8):
    storage_date += int(fw_id_data[40+i]) * 2**(56-i*8)
print('Storage timestamp: '+str(storage_date)+' ('+str(datetime.utcfromtimestamp(storage_date))+')')

if args.nomigrate == False:

    CONFIG_ADDRESS = (FIRMWARE_SECTOR_OFFSET+24) * spi.constants.SECTOR_SIZE
    
    print('Migrating configuration to new firmware')
    
    s = str()
    for i in fw_id_data[0:32]:
        s += '{:02x}'.format(i)

    new_cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+s+' as x')

    if prev_hash != 0:
        
        s = str()
        for i in prev_hash[0:32]:
            s += '{:02x}'.format(i)

        prev_cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+s+' as x')

        prev_prom_cfg = prom.read_data(CONFIG_ADDRESS, 256)
        prev_cfg.import_prom_data(prev_prom_cfg)

        print('Scanning for matching keys...')

        prev_network_keys = prev_cfg.get_network_keys()
        prev_write_keys = prev_cfg.get_write_keys()
        new_network_keys = new_cfg.get_network_keys()
        new_write_keys = new_cfg.get_write_keys()

        network_keys_in_prev_not_new = list()
        network_keys_in_both = list()
        network_keys_in_new_not_prev = list()

        write_keys_in_prev_not_new = list()
        write_keys_in_both = list()
        write_keys_in_new_not_prev = list()
        
        for i in new_network_keys:
            if i in prev_network_keys:
                network_keys_in_both.append(i)
            else:
                network_keys_in_new_not_prev.append(i)

        for i in prev_network_keys:
            if not(i in new_network_keys):
                network_keys_in_prev_not_new.append(i)

        for i in new_write_keys:
            if i in prev_write_keys:
                write_keys_in_both.append(i)
            else:
                write_keys_in_new_not_prev.append(i)

        for i in prev_write_keys:
            if not(i in new_write_keys):
                write_keys_in_prev_not_new.append(i)

        if args.verbose == True:
            print('')
            s = str()
            for i in network_keys_in_new_not_prev:
                s += i+', '
            print('Network keys not present in previous image (will be set to defaults): '+s)
                
            s = str()
            for i in network_keys_in_prev_not_new:
                s += i+', '
            print('Network keys not present in new image (will be discarded): '+s)
        
            s = str()
            for i in network_keys_in_both:
                s += i+', '
            print('Network keys present in both images (will be copied): '+s)

            s = str()
            for i in write_keys_in_new_not_prev:
                s += i+', '
            print('Write keys not present in previous image (will be set to defaults): '+s)

            s = str()
            for i in write_keys_in_prev_not_new:
                s += i+', '
            print('Write keys not present in new image (will be discarded): '+s)

            s = str()
            for i in write_keys_in_both:
                s += i+', '
            print('Write keys present in both images (will be copied): '+s)

        print('')
        print('Copying settings to new configuration...')
        
        for i in network_keys_in_both:
            new_cfg.set_network_value(i, prev_cfg.get_network_value(i))

        for i in write_keys_in_both:
            new_cfg.set_write_value(i, prev_cfg.get_write_value(i))

        if args.verbose == True:
            print('')
            print('Network configuration is now:')
            print('')
            new_cfg.print_network_cfg()
            print('')
            print('Write configuration is now:')
            print('')
            new_cfg.print_write_cfg()

    new_prom_cfg = new_cfg.export_prom_data()

    print('')
    if ( (prev_hash != 0) and (prev_prom_cfg == new_prom_cfg) ):
        print('No settings update required - data is identical')
    else:
        print('Updating PROM settings...')
    
        prom.sector_erase(CONFIG_ADDRESS)
        prom.page_program(new_prom_cfg, CONFIG_ADDRESS, True)

# Disconnect the PROM interface before doing a reboot
del prom
if args.reboot == True:
    if args.bootloader == True:
        print('Rebooting to new bootloader image')
        qf2_python.identifier.reboot_to_bootloader(args.target, args.verbose)
    else:
        print('Rebooting to new runtime image')
        qf2_python.identifier.reboot_to_runtime(args.target, args.verbose)
