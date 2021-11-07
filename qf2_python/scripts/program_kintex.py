#!/usr/bin/env python

import argparse

import qf2_python.identifier as identifier
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser

import qf2_python.configuration.jtag.xilinx_7_ultrascale as xilinx_7_ultrascale

# Fixed for this design
SEQUENCER_PORT = 50003

parser = argparse.ArgumentParser(description='Program Kintex-7 firmware directly', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', required=True, help='Firmware bitfile to program')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Verify we are in runtime
identifier.verifyInRuntime(args.target, args.verbose)

# Get an active interface
x = identifier.get_active_interface(args.target, args.verbose)
if x.get_read_value('MAIN_POWER_STATE') != 1:
        raise Exception('Board main power is currently off!')

# Initialise the chain control
chain = jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=1, speed=0)

print('There are', chain.num_devices(), 'devices in the chain:')

print('')
for i in range(0, chain.num_devices()):
        print(hex(chain.idcode(i))+' - '+ chain.idcode_resolve_name(chain.idcode(i)))
print('')

# Parse the bitfile and resolve the part type
print('Loading bitfile:', args.bit)
bitfile = xilinx_bitfile_parser.bitfile(args.bit)

print('Design name:', bitfile.design_name())
print('Device name:', bitfile.device_name())
print('Build date:', bitfile.build_date())
print('Build time:', bitfile.build_time())
print('Length:', bitfile.length(), 'bits')

print('')

matching_devices = list()
for i in range(0, chain.num_devices()):
        if bitfile.match_idcode(chain.idcode(i)):
                matching_devices.append(i)

if len(matching_devices) == 0:
        print('No devices matching bitfile found in JTAG chain')
        exit()

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
print('Defaulting device selection in chain from IDCODE')

print('Device selected for programming is in chain location:',str(device_choice))

# TODO: Make this more generic
# Restricted to Kintex 7
if str('Xilinx Kintex 7') in chain.idcode_resolve_name(chain.idcode(device_choice)):
        print('Xilinx 7 series & Ultrascale programming interface selected')
        interface = xilinx_7_ultrascale.interface(chain)
else:
        print('Not able to program this device')
        exit()

print('Programming...')
print('')

# Load the bitfile
interface.program(bitfile.data(), device_choice)
