#!/bin/env python

import argparse, time, ctypes
import qf2_python.identifier

# Test blocks
reboot_to_runtime = [
    0x3261,
    0x0000,  # Mutiboot address [15:0] (GENERAL1)
    0x3281,
    0x0320,  # Opcode & Mutiboot address [23:16] (GENERAL2)
    0x32A1,
    0x0000,  # Fallback address [15:0] (GENERAL3)
    0x32C1,
    0x0300,  # Opcode & Fallback address [23:16] (GENERAL4)
    0x30A1,  
    0x000E   # ICAP reboot
    ]

reboot_to_bootloader = [
    0x3261,
    0x0000,  # Mutiboot address [15:0] (GENERAL1)
    0x3281,
    0x0300,  # Opcode & Mutiboot address [23:16] (GENERAL2)
    0x32A1,
    0x0000,  # Fallback address [15:0] (GENERAL3)
    0x32C1,
    0x0300,  # Opcode & Fallback address [23:16] (GENERAL4)
    0x30A1,  
    0x000E   # ICAP reboot
    ]

# Write scratchpad register (GENERAL5)
write_scratchpad = [
    0x32E1,
    0xABCD
    ]

# READ 1 word template
READ_ONE = 0x2801

# Read CRC
read_crc = READ_ONE | 0

# Read STAT (6'h8)
read_stat = READ_ONE | (0x8 << 5)

# Read GENERAL5 (6'h17)
read_general5 = READ_ONE | (0x17 << 5)

parser = argparse.ArgumentParser(description='Test ICAP interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

#x.icap_write(write_scratchpad)
#x.icap_write(reboot_to_bootloader)

# Do an ICAP transaction
print hex(x.icap_read(read_general5))
#print hex(x.icap_read(read_stat))
