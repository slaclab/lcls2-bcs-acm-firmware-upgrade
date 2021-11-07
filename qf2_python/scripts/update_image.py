#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta

import qf2_python.identifier as identifier
import qf2_python.scripts.helpers as helpers
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Store Spartan-6 image in PROM', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', default=None, help='Firmware bitfile to store')
parser.add_argument('-n', '--nomigrate', default=False, action="store_true", help='Don\'t migrate configuration when updating firmware')
parser.add_argument('-i', '--image', default='K', type=str, help='Target image')
parser.add_argument('-r', '--reboot', default=False, action="store_true", help='Reboot automatically')
parser.add_argument('-f', '--force', default=False, action="store_true", help='Force update even if previous PROM data is unrecognized or corrupt')
parser.add_argument('-v', '--verbose', default=False, action="store_true", help='Verbose output')

args = parser.parse_args()

identifier.verifyInBootloader(args.target, args.verbose)

# Fixed for current hardware
SEQUENCER_PORT = 50003

# Validate the image argument and set the image offsets
if args.image == 'B':
    FIRMWARE_SECTOR_OFFSET = 0
    FIRMWARE_ID_ADDRESS = 23 * spi_constants.SECTOR_SIZE    
    CONFIG_ADDRESS = 25 * spi_constants.SECTOR_SIZE    
elif args.image == 'R':
    FIRMWARE_SECTOR_OFFSET = 32
    FIRMWARE_ID_ADDRESS = 55 * spi_constants.SECTOR_SIZE    
    CONFIG_ADDRESS = 56 * spi_constants.SECTOR_SIZE    
elif args.image == 'K':
    FIRMWARE_SECTOR_OFFSET = 65
    FIRMWARE_ID_ADDRESS = 64 * spi_constants.SECTOR_SIZE
else:
    raise Exception('Image argument \''+args.image+'\' not a recognized type, choices are B (Bootloader), R (Runtime) or K (Kintex)')
    
# Select default image to program if we are not erasing only
if args.bit == None:
    if args.image == 'B':
        args.bit = 'firmwares/spartan_bootloader.bit'
    elif args.image == 'R':
        args.bit = 'firmwares/spartan_runtime.bit'
    elif args.image == 'K':
        raise Exception('You must provide an image for the Kintex, there isn\'t a default')
    print('Bitfile argument was not provided, assuming default from firmwares directory ('+args.bit+')')

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Do integrity check and check current firmware hash, Spartan only
#if args.image != 'K':
print('Running PROM image integrity check...')
prev_hash = helpers.prom_integrity_check(prom, FIRMWARE_SECTOR_OFFSET, args.verbose)
if (prev_hash == 0) and (args.force == False):
    raise Exception('ERROR: Current PROM data failed integrity check. You must use \'--force\' to continue - will set PROM settings to defaults.')

if args.verbose == True:
    print('Loading bitfile: '+args.bit)

bitfile = xilinx_bitfile_parser.bitfile(args.bit)

if args.verbose == True:
    print('Design name: '+bitfile.design_name())
    print('Device name: '+bitfile.device_name())
    print('Build date: '+bitfile.build_date())
    print('Build time: '+bitfile.build_time())
    print('Length: '+str(bitfile.length()))

# Safety check to match bitfile to part
if args.image != 'K':
    if bitfile.device_name() != '6slx45tcsg324':
        raise Exception('ERROR: Bitfile device name \''+bitfile.device_name()+'\' is not a Spartan-6 FPGA')
else:
    if bitfile.device_name() != '7k160tffg676':
        raise Exception('ERROR: Bitfile device name \''+bitfile.device_name()+'\' is not a Kintex-7 FPGA')

if bitfile.padded_hash() == prev_hash:
    print('Bitfile hash is already stored in PROM and hash is valid. Comparing PROM data for exact match...')
    if ( helpers.prom_compare_check(prom, FIRMWARE_SECTOR_OFFSET, args.bit, args.verbose) != 0 ):
        print('PROM data matches, exiting')
        exit(0)
    print('Mismatch in PROM data - continuing')

print('Programming image')
prom.program_bitfile(args.bit, FIRMWARE_SECTOR_OFFSET)

# Generate a firwmare ID block
fw_id_data = helpers.generate_fw_id_data(args.bit)

#for i in fw_id_data:
#    print(hex(i))
#print('')

print('Erasing old firmware ID block')
prom.sector_erase(FIRMWARE_ID_ADDRESS)

print('Updating firmware ID block')
for i in range(0, len(fw_id_data) // 256):
    prom.page_program(fw_id_data[i * 256 : (i+1) * 256], i * 256 + FIRMWARE_ID_ADDRESS, True)

s = str()
for j in fw_id_data[0:32]:
    s += '{:02x}'.format(j)
print('SHA256: '+s)
    
build_date = 0
for i in range(0, 8):
    build_date += int(fw_id_data[32+i]) << ((7-i)*8)
print('Build timestamp: '+str(build_date)+' ('+str(datetime.utcfromtimestamp(build_date))+')')

storage_date = 0
for i in range(0, 8):
    storage_date += int(fw_id_data[40+i]) << ((7-i)*8)
print('Storage timestamp: '+str(storage_date)+' ('+str(datetime.utcfromtimestamp(storage_date))+')')

if args.image == 'K':
    length = 0
    for i in range(0, 3):
        length += int(fw_id_data[48+i]) << ((2-i)*8)
    print('Firmware length: '+str(length))

    s = str()
    for j in fw_id_data[52:56]:
        s += '{:02x}'.format(j)
    print('CRC32: '+s)

else:
    s = str()
    for j in fw_id_data[48:52]:
        s += '{:02x}'.format(j)
    print('CRC32: '+s)
    
# Migrate if not(nomigrate) and a Spartan image
if (args.nomigrate == False) and (args.image != 'K'):

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
        prev_cfg.import_firmware_prom_data(prev_prom_cfg)

        print('Scanning for matching keys...')

        prev_write_keys = prev_cfg.get_write_keys()
        new_write_keys = new_cfg.get_write_keys()

        write_keys_in_prev_not_new = list()
        write_keys_in_both = list()
        write_keys_in_new_not_prev = list()
        
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
        
        for i in write_keys_in_both:
            new_cfg.set_write_value(i, prev_cfg.get_write_value(i))

        if args.verbose == True:
            print('')
            print('Firmware configuration is now:')
            print('')
            new_cfg.print_write_cfg()

    new_prom_cfg = new_cfg.export_firmware_prom_data()

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
    if args.image == 'B':
        print('Rebooting to bootloader')
        identifier.reboot_to_bootloader(args.target, args.verbose)
    else:
        print('Rebooting to runtime')
        identifier.reboot_to_runtime(args.target, args.verbose)
