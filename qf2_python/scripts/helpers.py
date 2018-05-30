#!/usr/bin/env python

import time, sys, argparse, hashlib
from datetime import datetime, timedelta
from ..configuration.jtag import *
from ..configuration.spi import *

def prom_integrity_check(prom, offset, verbose):

    if verbose == True:
        print 'Performing PROM integrity check'
        
    FIRMWARE_ID_ADDRESS = (offset+23) * spi.constants.SECTOR_SIZE
    
    # Assuming Spartan-6 here
    # As the Spartan-6 bitstream length can vary slightly from version to version,
    # the hash is generated to the end of the sector
    prom_hash = prom.read_hash(offset * spi.constants.SECTOR_SIZE, 23 * spi.constants.SECTOR_SIZE)

    # Compare the current data with the previous to see if we have to erase
    pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)

    if verbose == True:
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
        if verbose == True:
            print 'PROM bitstream integrity OK'
        return prom_hash

    if verbose == True:
        print 'PROM bitstream integrity BAD'
    return 0


def prom_compare_check(prom, offset, bitfile, verbose):

    if verbose == True:
        print 'Performing PROM bitfile comparison check'
        
    FIRMWARE_ID_ADDRESS = (offset+23) * spi.constants.SECTOR_SIZE

    # Check hash and timestamps stored in PROM
    parser = xilinx_bitfile_parser.bitfile(bitfile)

    # Extract the build date and time from the bitfile and encode it
    build_date = int(time.mktime(datetime.strptime(parser.build_date() + ' ' + parser.build_time(), '%Y/%m/%d %H:%M:%S').timetuple()))

    # Pad the data to the block boundary
    data = parser.data()
    data += bytearray([0xFF]) * (spi.constants.SECTOR_SIZE - len(data) % spi.constants.SECTOR_SIZE)

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

    if verbose == True:
        print
        print 'Firmware ID from bitfile:'
        print

        print 'SHA256:',
        s = str()
        for i in sha256[0:32]:
            s += '{:02x}'.format(i)
        print s
        print 'Build timestamp:', build_date, '('+str(datetime.utcfromtimestamp(build_date))+')'

    # Compare bitfile with data stored in PROM
    prom.verify_bitfile(bitfile, offset)

    # Compare the current data with the previous to see if we have to erase
    pd = prom.read_data(FIRMWARE_ID_ADDRESS, 48)

    # Only check the first two, the third changes each time
    did_break = False
    for i in range(0, len(sha256)):
        if ( sha256[i] != pd[i] ):
            if ( pd[i] != 0xFF ):
                did_break = True
                break

    if verbose == True:
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
        if verbose == True:
            print 'Firmware ID matches'
        return pd[0:32]

    if verbose == True:
        print 'Firmware ID doesn\'t match'
    return 0
