#!/usr/bin/env python

import datetime
from socket import *

def my_exec_interface(x, target, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].interface(target, verbose)

def get_board_information(r, verbose=False):
    bootloader_hash = str()
    x = r[11:43]
    x.reverse()
    for i in x: bootloader_hash += '{:02x}'.format(i)

    runtime_hash = str()
    x = r[51:83]
    x.reverse()
    for i in x: runtime_hash += '{:02x}'.format(i)

    board_uid = str()
    x = r[83:92]
    x.reverse()
    for i in x: board_uid += '{:02x}'.format(i)
            
    j = 0
    for i in range(0, 8):
        j = j + (int(r[3+i]) << (i*8))
    bootloader_date = str(datetime.datetime.utcfromtimestamp(j))
        
    j = 0
    for i in range(0, 8):
        j = j + (int(r[43+i]) << (i*8))
    runtime_date = str(datetime.datetime.utcfromtimestamp(j))

    board_type = str()
    if r[1] == 0:
        board_type = 'BMB7_r1'
    elif r[1] == 1:
        board_type = 'QF2_pre'
    else:
        board_type = 'UNKNOWN'

    active_firmware = str()
    if r[2] == 0:
        active_firmware = 'Bootloader'
    elif r[2] == 1:
        active_firmware = 'Runtime'
    else:
        active_firmware = 'UNKNOWN'

    ret = {
        'Board UID' : board_uid,
        'Bootloader SHA256' : bootloader_hash,
        'Runtime SHA256' : runtime_hash,
        'Bootloader build date' : bootloader_date,
        'Runtime build date' : runtime_date,
        'Board type' : board_type,
        'Active firmware' : active_firmware
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

def get_active_interface(target, r, verbose):
    x = get_board_information(r, verbose)

    # Map the SHA256 to target based on the currently active firmware
    h = str()
    if x['Active firmware'] == 'Bootloader':
        h = x['Bootloader SHA256']
    elif x['Active firmware'] == 'Runtime':
        h = x['Runtime SHA256']
        
    # Return an interface
    return my_exec_interface('import qf2_python.'+x['Board type']+'.v_'+h+' as x', target, verbose)
