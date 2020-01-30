#!/usr/bin/env python

import argparse

import qf2_python.identifier as identifier
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser

print('TODO: Merge 7 series programming code')
print('TODO: Add header select for programming')
print('')

# Fixed for S6 programming interface
SEQUENCER_PORT = 50003

parser = argparse.ArgumentParser(description='Program an external device over JTAG via PMOD C', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', required=True, help='Firmware bitfile to program')
parser.add_argument('-s', '--speed', type=int, default=int(10), help='Clock speed divider (smaller is faster)')
parser.add_argument('-v', '--verbose', default=False, action="store_true", help='Verbose output')
args = parser.parse_args()

# Verify we are in the bootloader
identifier.verifyInBootloader(args.target, args.verbose)

# This feature requires at least 0.7.0+1
identifier.verifyFirmwareVersionRecentAs(0, 7, 0, 1, args.target, args.verbose)

# Initialise the chain control
chain = jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=1, speed=args.speed)

print('There are '+str(chain.num_devices())+' devices in the chain:')

print('')
for i in range(0, chain.num_devices()):
        print(hex(chain.idcode(i))+' - '+chain.idcode_resolve_name(chain.idcode(i)))
print('')

# Parse the bitfile and resolve the part type
print('Loading bitfile:'+args.bit)
bitfile = xilinx_bitfile_parser.bitfile(args.bit)

print('Design name: '+bitfile.design_name())
print('Device name: '+bitfile.device_name())
print('Build date: '+bitfile.build_date())
print('Build time: '+bitfile.build_time())
print('Length: '+str(bitfile.length())+' bits')
print('')

matching_devices = list()
for i in range(0, chain.num_devices()):
        if bitfile.match_idcode(chain.idcode(i)):
                matching_devices.append(i)

if len(matching_devices) == 0:
        raise Exception('No devices matching bitfile found in JTAG chain')

if len(matching_devices) > 1:
        raise Exception('Multiple devices in chain is not currently supported')

# Default to first (and only) entry
device_choice = matching_devices[0]

# Override choice from argument line if there's more than one device
#if len(matching_devices) > 1:
#        if len(sys.argv) < 4:
#                print 'More than one matching FPGA in device chain - you must add a chain ID to the arguments'
#                exit()

#        choice_made = False
#        for i in matching_devices:
#                if i == int(sys.argv[3]):
#                        device_choice = i
#                        choice_made = True

#        if choice_made == False:
#                print 'No matching device selection found that corresponds to JTAG chain'
#                exit()
#else:
#print('Defaulting device selection in chain from IDCODE')
#print('Device selected for programming is in chain location:'+str(device_choice))

if str('Xilinx Virtex 5') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx Virtex 5 interface selected')
        interface = xilinx_virtex_5.interface(chain)
elif str('Xilinx Spartan 6') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx Spartan 6 interface selected')
        interface = xilinx_spartan_6.interface(chain)
elif str('Xilinx Artix 7') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx 7 series interface selected')
        interface = xilinx_7_series.interface(chain)
elif str('Xilinx Kintex 7') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx Kintex 7 interface selected')
        interface = xilinx_kintex_7.interface(chain)
elif str('Xilinx Virtex 7') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx Virtex 7 interface selected')
        interface = xilinx_virtex_7.interface(chain)
else:
        print('Not able to program this device')
        exit()

print('Programming...')
print

# Load the bitfile
interface.program(bitfile.data(), device_choice)
