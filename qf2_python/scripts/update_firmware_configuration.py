#!/usr/bin/env python

import argparse

import qf2_python.identifier as identifier
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Store Spartan-6 configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Store bootloader')
parser.add_argument('-r', '--reboot', action="store_true", default=False, help='Reboot automatically')
parser.add_argument('-d', '--defaults', action="store_true", help='Reset to defaults')
parser.add_argument('-j', '--json', help='JSON settings file')
parser.add_argument('-s', '--settings', nargs='+', action='append', type=lambda kv: kv.split("="), dest='settings')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for PROM interface')

args = parser.parse_args()

# Check that the lock is only applied to the bootloader
#    if args.bootloader == False:
#if args.lock == True:
#        raise Exception('ERROR: Lock argument can only be used for the bootloader')

# Chose firmware location
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0
    FIRMWARE_ID_ADDRESS = 23 * spi_constants.SECTOR_SIZE
    CONFIG_ADDRESS = 25 * spi_constants.SECTOR_SIZE
else:
    FIRMWARE_SECTOR_OFFSET = 32
    FIRMWARE_ID_ADDRESS = 55 * spi_constants.SECTOR_SIZE
    CONFIG_ADDRESS = 56 * spi_constants.SECTOR_SIZE

SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Check the stored SHA256 to see what configuration space we should be using
pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)

s = str()
for i in pd[0:32]:
    s += '{:02x}'.format(i)
print('Stored SHA256: '+s)

print('Selecting matching configuration interface')
cfg = my_exec_cfg('import qf2_python.QF2_pre.v_'+s+' as x', args.verbose)

# TODO - Warn on mismatch with running firmware
#x = qf2_python.identifier.get_board_information(args.target, args.verbose)

pd = prom.read_data(CONFIG_ADDRESS, 256)

if args.defaults == False:
    print('Importing stored Spartan-6 configuration settings')
    cfg.import_firmware_prom_data(pd)

    if args.json != None:
        print('Importing JSON file settings from '+args.json)
        import json
        with open(args.json) as json_data:
            d = json.load(json_data)
            for i_k, i_v in d.iteritems():
                print(str(i_k)+' : '+str(i_v))
                if type(i_v) == unicode:
                    i_v = str(i_v)
                    unknown_key = True
                #if cfg.is_network_key(i_k):
                #    unknown_key = False
                #    cfg.set_network_value(i_k, i_v)
                if cfg.is_write_key(i_k):
                    unknown_key = False
                    cfg.set_write_value(i_k, i_v)
                if unknown_key == True:
                    raise Exception('Unknown key '+i_k)

    if args.settings != None:
        print('Adding command line settings')
        for i in args.settings[0]:
            print(i[0]+' : '+i[1])
            unknown_key = True
            #if cfg.is_network_key(i[0]):
            #    unknown_key = False
            #    cfg.set_network_value(i[0], i[1])
            if cfg.is_write_key(i[0]):
                unknown_key = False
                cfg.set_write_value(i[0], i[1])
            if unknown_key == True:
                raise Exception('Unknown key '+i[0])

if args.verbose == True:
    print('Updated settings are:')
    #cfg.print_network_cfg()
    cfg.print_write_cfg()

print('Exporting PROM settings')
x = cfg.export_firmware_prom_data()

if ( x == pd ):
    print('Values already programmed')
    # Disconnect the PROM interface before doing a reboot
    del prom
    if args.reboot == True:
        if args.bootloader == True:
            print('Rebooting with new bootloader settings')
            identifier.reboot_to_bootloader(args.target, args.verbose)
        else:
            print('Rebooting with new runtime settings')
            identifier.reboot_to_runtime(args.target, args.verbose)
    exit()

print('Updating PROM settings')

prom.sector_erase(CONFIG_ADDRESS)
prom.page_program(x, CONFIG_ADDRESS, True)

# Disconnect the PROM interface before doing a reboot
del prom
if args.reboot == True:
    if args.bootloader == True:
        print('Rebooting with new bootloader settings')
        identifier.reboot_to_bootloader(args.target, args.verbose)
    else:
        print('Rebooting with new runtime settings')
        identifier.reboot_to_runtime(args.target, args.verbose)
