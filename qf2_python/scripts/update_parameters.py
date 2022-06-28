#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath('../users'))

import argparse, zlib

import qf2_python.identifier as identifier

import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

parser = argparse.ArgumentParser(description='Update BCS ACM configuration stored on FLASH', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-j', '--json', type=str, required=True, help='JSON settings file')
parser.add_argument('-v', '--verbose', default=False, action="store_true", help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for PROM interface')

args = parser.parse_args()

# Make sure we are in the bootloader - the PROM isn't accessible otherwise
identifier.verifyInBootloader(args.target, args.verbose)

# Settings list in configuration space
# Position in table indicates 32-bit offset
SETTINGS_TABLE = [
    ['BeamLim', 32, False], # 32b, unsigned
    ['ConfLim', 32, False], # 32b, unsigned
    ['PltMagLimHi', 26, False], # 26b, unsigned
    ['PltMagLimLo', 26, False], # 26b, unsigned
    ['CnfMagLim', 26, False], # 26b, unsigned
    ['DifPhsOffset', 26, True], # 26b, signed
    ['DifMagLimHi', 27, True], # 27b, signed
    ['DifMagLimLo', 27, True], # 27b, signed

    ['DifPhsLimHi', 26, True], # 26b, signed
    ['DifPhsLimLo', 26, True], # 26b, signed
    ['BufTrigLim' , 22, False], # 22b, unsigned
    ['WFPcktDelay', 16, False], # 16b, unsigned
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],
    ['ModbusSlaveAddress', 8, False], # 8b, unsigned
    ['ModbusInboundCRC', 16, False], # 16b, unsigned
    ]

def findSetting(name):
    for i in range(len(SETTINGS_TABLE)):
        if SETTINGS_TABLE[i][0] == name:
            return i
    raise Exception('Setting name cannot be found')

def usedLen(t):
    count = 0
    for i in t:
        if len(i) == 3:
            count += 1
    return count
    
# Pre-sized output data list
outputs = bytearray([0]) * 256

# Open the JSON file and check all the required setting data is there
print('Importing JSON file settings from '+args.json)
import json
with open(args.json) as json_data:
    d = json.load(json_data)

    if usedLen(SETTINGS_TABLE) != len(d):
        print('Number of entries in settings table does not match json file')
        exit()

    for i_k, i_v in d.items(): # Was iteritems() in python2

        if type(i_v) != int:
            print('Setting type \''+ i_k +'\' is not an integer in the JSON file')
            exit()

        # Look up settings information
        tloc = findSetting(i_k)
        tinfo = SETTINGS_TABLE[tloc][1:3]
        signed = tinfo[1]
        nbits = tinfo[0]
        value = i_v

        # Sign check
        if signed:
            # Signed
            if (i_v < -2**(nbits-1)) or (i_v > 2**(nbits-1)-1):
                print('Value of \''+ i_k +'\' is outside allowed range')
                exit()
            # Map the answer to the bit range
            value = value & (2**nbits-1)
        else:
            # Unsigned
            if (i_v < 0) or (i_v > 2**nbits-1):
                print('Value of \''+ i_k +'\' is outside allowed range')
                exit()
            # No conversion required

        # Pack value into output data
        outputs[tloc*4] = value & 0xFF
        outputs[tloc*4+1] = (value>>8) & 0xFF
        outputs[tloc*4+2] = (value>>16) & 0xFF
        outputs[tloc*4+3] = (value>>24) & 0xFF

        print(str(i_k)+' : '+str(i_v)+' -> '+str(hex(value)))

# Settings are stored at the beginning of the upper half of the PROM
# The Kintex firmware and Spartan firmware are stored in the lower half
SETTINGS_SECTOR_OFFSET = 256
SETTINGS_ADDRESS = 256 * spi_constants.SECTOR_SIZE

# CRC-32 residue should be 0xC704DD7B if there is already valid data & checksum stored
CRC_RESIDUE = 0xC704DD7B

# JTAG / SPI sequencer port
SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Calculate CRC
crc = zlib.crc32(outputs[0:252]) & 0xFFFFFFFF

# Append CRC
for i in range(4):
    byte = (crc >> (8*i)) & 0xFF
    outputs[252+i] = byte

if args.verbose:
    s = 'Output block is: '
    for i in outputs:
        s = s + '{:02x}'.format(i)
    print(s)

pd = prom.read_data(SETTINGS_ADDRESS, 256)
if pd == outputs:
    print('PROM data already matches these settings - no overwrite required')
    exit()

# We have to erase a sector (64k), even to erase just a page
print('Erasing sector')
prom.sector_erase(SETTINGS_ADDRESS)
print('Writing page')
prom.page_program(outputs, SETTINGS_ADDRESS, True)
