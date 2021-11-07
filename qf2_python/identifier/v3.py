#!/usr/bin/env python

import datetime
from socket import *

def my_exec_interface(x, target, expected_version, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    
    # Check expected version
    found_version = str(ldict['x'].MAJOR_VERSION) + '.' + str(ldict['x'].MINOR_VERSION_1) + '.' + str(ldict['x'].MINOR_VERSION_2) + '+' + str(ldict['x'].MINOR_VERSION_3)

    if found_version != expected_version:
        raise Exception('Firmware version mismatch - currently running firmware is ' + expected_version + ', but the PROM version last checked during load was ' + found_version + '. This has likely happened because you either loaded an initial Spartan-6 firmware using JTAG and the PROM is empty, or you have updated the PROM image but not rebooted to the new version. To ensure correct operation, make sure your PROM is correctly updated, then reboot your board.')
    
    return ldict['x'].interface(target, verbose)

def get_board_information(r, verbose=False):

    board_type = str()
    if r[1] == 0:
        board_type = 'BMB7_r1'
    elif r[1] == 1:
        board_type = 'QF2_pre'
    else:
        board_type = 'UNKNOWN'

    active_firmware = str()
    if r[2] == 0:
        active_firmware_type = 'Bootloader'
    elif r[2] == 1:
        active_firmware_type = 'Runtime'
    elif r[2] == 2:
        active_firmware_type = 'HiRel Bootloader'
    elif r[2] == 3:
        active_firmware_type = 'HiRel Runtime'
    else:
        active_firmware_type = 'UNKNOWN'

    active_firmware_version = str(r[6]) + '.' + str(r[5]) + '.' + str(r[4]) + '+' + str(r[3])

    j = 0
    for i in range(0, 8):
        j = j + (int(r[7+i]) << (i*8))
    if j == (2**64-1):
        bootloader_storage_date = 'NOT SET'
    else:
        bootloader_storage_date = str(datetime.datetime.utcfromtimestamp(j))

    j = 0
    for i in range(0, 8):
        j = j + (int(r[15+i]) << (i*8))
    if j == (2**64-1):
        bootloader_build_date = 'NOT SET'
    else:
        bootloader_build_date = str(datetime.datetime.utcfromtimestamp(j))
    
    bootloader_hash = str()
    x = r[23:55]
    x.reverse()
    for i in x: bootloader_hash += '{:02x}'.format(i)
    if bootloader_hash == 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff':
        bootloader_hash = 'NOT SET'

    j = 0
    for i in range(0, 8):
        j = j + (int(r[55+i]) << (i*8))
    if j == (2**64-1):
        runtime_storage_date = 'NOT SET'
    else:
        runtime_storage_date = str(datetime.datetime.utcfromtimestamp(j))

    j = 0
    for i in range(0, 8):
        j = j + (int(r[63+i]) << (i*8))
    if j == (2**64-1):
        runtime_build_date = 'NOT SET'
    else:
        runtime_build_date = str(datetime.datetime.utcfromtimestamp(j))
    
    runtime_hash = str()
    x = r[71:103]
    x.reverse()
    for i in x: runtime_hash += '{:02x}'.format(i)
    if runtime_hash == 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff':
        runtime_hash = 'NOT SET'
    
    j = 0
    for i in range(0, 8):
        j = j + (int(r[103+i]) << (i*8))

    # Check for undefined
    if j == (2**64-1):
        kintex_storage_date = 'NOT SET'
    else:
        kintex_storage_date = str(datetime.datetime.utcfromtimestamp(j))

    j = 0
    for i in range(0, 8):
        j = j + (int(r[111+i]) << (i*8))

    if j == (2**64-1):
        kintex_build_date = 'NOT SET'
    else:
        kintex_build_date = str(datetime.datetime.utcfromtimestamp(j))
    
    kintex_hash = str()
    x = r[119:151]
    x.reverse()
    for i in x: kintex_hash += '{:02x}'.format(i)
    if kintex_hash == 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff':
        kintex_hash = 'NOT SET'

    j = 0
    for i in range(0, 3):
        j = j + (int(r[151+i]) << (i*8))
    kintex_length = str(j)
    if j == (2**24-1):
        kintex_length = 'NOT SET'
    
    board_uid = str()
    x = r[154:163]
    x.reverse()
    for i in x: board_uid += '{:02x}'.format(i)
    
    ret = {
        'Board UID' : board_uid,

        'Bootloader SHA256' : bootloader_hash,
        'Runtime SHA256' : runtime_hash,
        'Kintex SHA256' : kintex_hash,
        
        'Bootloader build date' : bootloader_build_date,
        'Runtime build date' : runtime_build_date,
        'Kintex build date' : kintex_build_date,

        'Bootloader storage date' : bootloader_storage_date,
        'Runtime storage date' : runtime_storage_date,
        'Kintex storage date' : kintex_storage_date,

        'Kintex length' : kintex_length,
        
        'Board type' : board_type,
        'Active firmware type' : active_firmware_type,
        'Active firmware version' : active_firmware_version
        }

    return ret

def reboot_to_runtime(target, verbose=False, wait_for_reboot=False):

    x = bytearray([0x81])
    TempSock = socket(AF_INET,SOCK_DGRAM)
    TempSock.sendto(x,(target,50000))
    TempSock.close()

    if wait_for_reboot == False:
        return

    # Wait two seconds for board to enter reset phase
    time.sleep(2)
                
    # Loop wait for reboot
    print('Waiting for board to reconnect...')
    x = bytearray([0x0])
    TempSock = socket(AF_INET,SOCK_DGRAM)
    TempSock.bind(("0.0.0.0", 0))
    TempSock.settimeout(1)

    count = 0
    for count in range(0, 15):
        try:
            TempSock.sendto(x,(target, 50000))
            TempSock.recv(1000)
            break
        except KeyboardInterrupt:
            print('Ctrl-C detected')
            exit(0)
        except:
            continue

    if count == 14:
        raise Exception('Reboot failed')

    print('Reboot complete')
    TempSock.close()

def reboot_to_bootloader(target, verbose=False, wait_for_reboot=False):

    x = bytearray([0x01])
    TempSock = socket(AF_INET,SOCK_DGRAM)
    TempSock.sendto(x,(target,50000))
    TempSock.close()

    if wait_for_reboot == False:
        return

    # Wait two seconds for board to enter reset phase
    time.sleep(2)
                
    # Loop wait for reboot
    print('Waiting for board to reconnect...')
    x = bytearray([0x0])
    TempSock = socket(AF_INET,SOCK_DGRAM)
    TempSock.bind(("0.0.0.0", 0))
    TempSock.settimeout(1)

    count = 0
    for count in range(0, 15):
        try:
            TempSock.sendto(x,(target, 50000))
            TempSock.recv(1000)
            break
        except KeyboardInterrupt:
            print('Ctrl-C detected')
            exit(0)
        except:
            continue

    if count == 14:
        raise Exception('Reboot failed')

    print('Reboot complete')
    TempSock.close()

def get_active_interface(target, r, verbose, development):
    x = get_board_information(r, verbose)

    # Map the SHA256 to target based on the currently active firmware
    # Alternatively, use development code without using the SHA256
    h = str()
    if development == False:
        if x['Active firmware type'] == 'Bootloader':
            h = x['Bootloader SHA256']
        elif x['Active firmware type'] == 'Runtime':
            h = x['Runtime SHA256']
        elif x['Active firmware type'] == 'HiRel Bootloader':
            h = x['Bootloader SHA256']
        elif x['Active firmware type'] == 'HiRel Runtime':
            h = x['Runtime SHA256']
        h = '.v_'+h
    else:
        if x['Active firmware type'] == 'Bootloader':
            h = '.dev_bootloader'
        elif x['Active firmware type'] == 'Runtime':
            h = '.dev_runtime'
        elif x['Active firmware type'] == 'HiRel Bootloader':
            h = '.dev_bootloader'
        elif x['Active firmware type'] == 'HiRel Runtime':
            h = '.dev_runtime'
            
    # Return an interface
    return my_exec_interface('import qf2_python.'+x['Board type']+h+' as x',
                             target,
                             x['Active firmware version'],
                             verbose)

def verifyInBootloader(r, verbose):
    x = get_board_information(r, verbose)    
    if (x['Active firmware type'] != 'Bootloader') and (x['Active firmware type'] != 'HiRel Bootloader'):
        raise Exception('Spartan bootloader must be running')

def verifyInRuntime(r, verbose):
    x = get_board_information(r, verbose)    
    if (x['Active firmware type'] != 'Runtime') and (x['Active firmware type'] != 'HiRel Runtime'):
        raise Exception('Spartan runtime must be running')

def verifyFirmwareVersionRecentAs(v1, v2, v3, v4, r, verbose):

    # Turn the version check into a numerical comparison
    a = (int(r[6]) << 24) | (int(r[5]) << 16) | (int(r[4]) << 8) | int(r[3])
    b = (int(v1) << 24) | (int(v2) << 16) | (int(v3) << 8) | int(v4)

    if a >= b:
        return
    
    active_firmware_version = str(r[6]) + '.' + str(r[5]) + '.' + str(r[4]) + '+' + str(r[3])
    expected_firmware_version = str(v1) + '.' + str(v2) + '.' + str(v3) + '+' + str(v4)    
    raise Exception('Active firmware version ('+active_firmware_version+') must be at least as recent as '+expected_firmware_version)

