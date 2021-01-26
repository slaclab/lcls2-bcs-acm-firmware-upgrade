#!/usr/bin/env python

import time, sys, argparse, hashlib
from datetime import datetime, timedelta

import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

def generate_fw_id_data(bitfile):

    # Initialize the parser
    parser = xilinx_bitfile_parser.bitfile(bitfile)

    # Get the current date & time from NTP
    # Otherwise use local
    storage_date = 0

    try:
        import ntplib
        try:
            c = ntplib.NTPClient()
            response = c.request('0.pool.ntp.org', version=3)
            storage_date = int(response.tx_time)
        except ntplib.NTPException:
            print('Timeout on NTP request, using local clock instead')
            storage_date = int(time.time())
    except:
        print('ntplib does not appear to be installed, using local clock instead')
        storage_date = int(time.time())

    # Extract the build date and time from the bitfile and encode it
    build_date = int(time.mktime(datetime.strptime(parser.build_date() + ' ' + parser.build_time(), '%Y/%m/%d %H:%M:%S').timetuple()))

    # Get padded hash of bitfile data
    sha256 = parser.padded_hash()

    # Append build date
    sha256.append((build_date >> 56) & 0xFF)
    sha256.append((build_date >> 48) & 0xFF)
    sha256.append((build_date >> 40) & 0xFF)
    sha256.append((build_date >> 32) & 0xFF)
    sha256.append((build_date >> 24) & 0xFF)
    sha256.append((build_date >> 16) & 0xFF)
    sha256.append((build_date >> 8) & 0xFF)
    sha256.append((build_date) & 0xFF)

    # Append storage date
    sha256.append((storage_date >> 56) & 0xFF)
    sha256.append((storage_date >> 48) & 0xFF)
    sha256.append((storage_date >> 40) & 0xFF)
    sha256.append((storage_date >> 32) & 0xFF)
    sha256.append((storage_date >> 24) & 0xFF)
    sha256.append((storage_date >> 16) & 0xFF)
    sha256.append((storage_date >> 8) & 0xFF)
    sha256.append((storage_date) & 0xFF)

    # If a Kintex firmware, we include the length
    if parser.device_name() == '7k160tffg676':
        length = parser.length()
        sha256.append((length >> 16) & 0xFF)
        sha256.append((length >> 8) & 0xFF)
        sha256.append(length & 0xFF)

    #for i in range(0, len(sha256)):
    #    print(str(i)+' '+str(hex(sha256[i])))
        
    # Pad to page boundary
    sha256 += bytearray([0xFF]) * (256 - len(sha256) % 256)

    return sha256

def prom_integrity_check(prom, offset, verbose):

    if verbose == True:
        print('Performing PROM integrity check')

    if offset != 65:

        FIRMWARE_ID_ADDRESS = (offset+23) * spi_constants.SECTOR_SIZE
    
        # Assuming Spartan-6 here
        # As the Spartan-6 bitstream length can vary slightly from version to version,
        # the hash is generated to the end of the sector
        prom_hash = prom.read_hash(offset * spi_constants.SECTOR_SIZE, 23 * spi_constants.SECTOR_SIZE)

        # Compare the current data with the previous to see if we have to erase
        pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)
        
    else:
        FIRMWARE_ID_ADDRESS = (offset-1) * spi_constants.SECTOR_SIZE
    
        # Assuming Kintex-7 here
        prom_hash = prom.read_hash(offset * spi_constants.SECTOR_SIZE, 103 * spi_constants.SECTOR_SIZE)

        # Compare the current data with the previous to see if we have to erase
        pd = prom.read_data(FIRMWARE_ID_ADDRESS, 32)
        
    if verbose == True:
        
        s = 'Bitstream SHA256: '
        for i in prom_hash[0:32]:
            s += '{:02x}'.format(i)
        print(s)

        s = 'Stored SHA256: '
        for i in pd[0:32]:
            s += '{:02x}'.format(i)
        print(s)

    if prom_hash == pd:
        if verbose == True:
            print('PROM bitstream integrity OK')
        return prom_hash

    if verbose == True:
        print('PROM bitstream integrity BAD')
    return 0

def prom_compare_check(prom, offset, bitfile, verbose):

    if verbose == True:
        print('Performing PROM bitfile comparison check')

    if offset != 65:
        FIRMWARE_ID_ADDRESS = (offset+23) * spi_constants.SECTOR_SIZE
    else:
        FIRMWARE_ID_ADDRESS = (offset-1) * spi_constants.SECTOR_SIZE
    
    # Check hash and timestamps stored in PROM
    fw_id_data = generate_fw_id_data(bitfile)

    if verbose == True:
        print('')
        print('Firmware ID from bitfile:')
        print('')

        s = 'SHA256: '
        for i in fw_id_data[0:32]:
            s += '{:02x}'.format(i)
        print(s)

        build_date = 0
        for i in range(0, 8):
            build_date += int(fw_id_data[32+i]) << ((7-i)*8)
        print('Build timestamp: '+str(build_date)+' ('+str(datetime.utcfromtimestamp(build_date))+')')

    # Compare bitfile with data stored in PROM
    print('')
    print('Comparing bitfile with PROM data...')
    prom.verify_bitfile(bitfile, offset)

    # Compare the current data with the previous to see if we have to erase
    pd = prom.read_data(FIRMWARE_ID_ADDRESS, 51)

    if verbose == True:
        print('')
        print('Firmware ID stored in PROM:')
        print('')

        s = str()
        for i in pd[0:32]:
            s += '{:02x}'.format(i)
        print('SHA256: '+s)

        build_date = 0
        for i in range(0, 8):
            build_date += int(pd[32+i]) << ((7-i)*8)
        print('Build timestamp: '+str(build_date)+' ('+str(datetime.utcfromtimestamp(build_date))+')')

        storage_date = 0
        for i in range(0, 8):
            storage_date += int(pd[40+i]) << ((7-i)*8)
        print('Storage timestamp: '+str(storage_date)+' ('+str(datetime.utcfromtimestamp(storage_date))+')')
        print

    #for i in range(0, 51):
    #    print(str(i)+' '+hex(fw_id_data[i])+' '+hex(pd[i]))
    #print('')

    # Check everything but the storage date matches
    if (pd[0:40] == fw_id_data[0:40]) and (pd[48:51] == fw_id_data[48:51]):
        if verbose == True:
            print('Firmware ID matches')
        return pd[0:32]

    if verbose == True:
        print('Firmware ID doesn\'t match')
    return 0
