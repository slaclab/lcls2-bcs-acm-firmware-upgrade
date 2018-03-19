#!/usr/bin/env python

# Alternative way of dealing with python package semantics
# Append package path if it isn't already known
#if __name__ == '__main__' and __package__ is None:
#    import sys, os.path as path
#    print(path.dirname(path.dirname(path.abspath(__file__))))
#    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import time, sys, argparse, hashlib
from datetime import datetime, timedelta
from ..configuration.jtag import *
from ..configuration.spi import *

def prom_integrity_check(prom):
    
    # Assuming Spartan-6 here
    # As the Spartan-6 bitstream length can vary slightly from version to version,
    # the hash is generated to the end of the sector
    prom_hash = prom.read_hash(FIRMWARE_SECTOR_OFFSET * spi.SECTOR_SIZE, 23 * spi.SECTOR_SIZE)

    # Compare the current data with the previous to see if we have to erase
    pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)

    print 'Bitstream SHA256:',
    s = str()
    for i in prom_hash[0:32]:
        s += '{:02x}'.format(i)
    print s

    print 'Stored SHA256:',
    s = str()
    for i in pd[0:32]:
        s += '{:02x}'.format(i)
    print s

    if prom_hash == pd:
        print 'PROM bitstream integrity OK'
        exit(0)

    print 'PROM bitstream integrity BAD'
    exit(1)    

def prom_compare_check(prom, bitfile):

    # Compare bitfile with data stored in PROM
    prom.verify_bitfile(bitfile, FIRMWARE_SECTOR_OFFSET)

    # Check hash and timestamps stored in PROM
    parser = xilinx_bitfile_parser.bitfile(bitfile)

    # Extract the build date and time from the bitfile and encode it
    build_date = int(time.mktime(datetime.strptime(parser.build_date() + ' ' + parser.build_time(), '%Y/%m/%d %H:%M:%S').timetuple()))

    # Pad the data to the block boundary
    data = parser.data()
    data += bytearray([0xFF]) * (spi.SECTOR_SIZE - len(data) % spi.SECTOR_SIZE)

    # Calculate SHA256 of bitfile
    m = hashlib.sha256()
    m.update(data)
    sha256 = bytearray(m.digest())

    # Append build date
    sha256.append((build_date >> 56) & 0xFF)
    sha256.append((build_date >> 48) & 0xFF)
    sha256.append((build_date >> 40) & 0xFF)
    sha256.append((build_date >> 32) & 0xFF)
    sha256.append((build_date >> 24) & 0xFF)
    sha256.append((build_date >> 16) & 0xFF)
    sha256.append((build_date >> 8) & 0xFF)
    sha256.append((build_date) & 0xFF)

    # Compare the current data with the previous to see if we have to erase
    pd = prom.read_data(FIRMWARE_ID_ADDRESS, 48)

    # Only check the first two, the third changes each time
    did_break = False
    for i in range(0, len(sha256)):
        if ( sha256[i] != pd[i] ):
            if ( pd[i] != 0xFF ):
                did_break = True
                break

    print
    print 'Firmware ID from bitfile:'
    print

    print 'SHA256:',
    s = str()
    for i in sha256[0:32]:
        s += '{:02x}'.format(i)
    print s
    print 'Build timestamp:', build_date, '('+str(datetime.utcfromtimestamp(build_date))+')'

    print
    print 'Firmware ID stored in PROM:'
    print

    print 'SHA256:',
    s = str()
    for i in pd[0:32]:
        s += '{:02x}'.format(i)
    print s

    build_date = 0
    for i in range(0, 8):
        build_date += int(pd[32+i]) * 2**(56-i*8)
    print 'Build timestamp:', build_date, '('+str(datetime.utcfromtimestamp(build_date))+')'

    storage_date = 0
    for i in range(0, 8):
        storage_date += int(pd[40+i]) * 2**(56-i*8)
    print 'Storage timestamp:', storage_date, '('+str(datetime.utcfromtimestamp(storage_date))+')'
    print

    if did_break == False:
        print 'Firmware ID matches'
        exit(0)

    print 'Firmware ID doesn\'t match'
    exit(1)    

parser = argparse.ArgumentParser(description='Verify Spartan-6 image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', help='Bitfile to compare against')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Verify bootloader')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

# Chose firmware location (bootloader or runtime)
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0
else:
    FIRMWARE_SECTOR_OFFSET = 32

FIRMWARE_ID_ADDRESS = (FIRMWARE_SECTOR_OFFSET+23) * spi.SECTOR_SIZE
SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True))

if prom.prom_size() != 25:
    print 'ERROR: PROM size incorrect, read',prom.prom_size()
    exit(1)

# Read the VCR and VECR
if args.verbose == True:
    print 'PROM ID (0x20BA, Capacity=0x19, EDID+CFD length=0x10, EDID (2 bytes), CFD (14 bytes)',
    print 'VCR (should be 0xfb by default):',hex(prom.read_register(spi.RDVCR, 1)[0])
    print 'VECR (should be 0xdf):',hex(prom.read_register(spi.RDVECR, 1)[0])
    print 'PROM size: 256Mb == 500 x 64KB blocks'

# If not bitfile provided for comparison, do an integrity check
if args.bit == None:
    print 'No bitfile provided - performing PROM integrity check'
    prom_integrity_check(prom)
else:
    print 'Bitfile provided - performing PROM integrity check'
    prom_compare_check(prom, args.bit)


