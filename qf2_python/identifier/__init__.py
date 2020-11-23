#!/usr/bin/env python

__all__ = [
    'v0',
    'v1',
    'v2',
    'v3',
    ]

import socket

HIGHEST_VERSION = 3

def __query_board(target, verbose=False):
    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPSock.bind(("0.0.0.0", 0))
    UDPSock.settimeout(1)

    bytes = bytearray([0])
    #data = str(bytes)

    UDPSock.sendto(bytes,(target,50000))
    result = UDPSock.recv(1400)
    UDPSock.close()

    r = bytearray(result)
    r.reverse()

    if verbose == True:
        print('Board ID packet format: '+str(r[0]))

    if r[0] > HIGHEST_VERSION:
        raise Exception('ERROR - unrecognized board ID packet format ('+str(r[0])+')')

    return r

def reboot_to_runtime(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')

    # Make sure we are not in runtime - you can only reboot to runtime from
    # the bootloader in this version
    x = ldict['x'].get_board_information(r, verbose)
    if x['Active firmware type'] == 'Runtime':
        raise Exception('You cannot reboot to a runtime image if you are already in the runtime. Reboot to the bootloader first, then back to the runtime.')
    
    # Reboot to the runtime
    ldict['x'].reboot_to_runtime(target, verbose)

def reboot_to_bootloader(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)
    
    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')

    # Reboot to the bootloader
    ldict['x'].reboot_to_bootloader(target, verbose)
    
def get_board_information(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].get_board_information(r, verbose)

    # Return the instance
    return x

def get_active_interface(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].get_active_interface(target, r, verbose)

    # Return the instance
    return x

def verifyInBootloader(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].verifyInBootloader(r, verbose)

def verifyInRuntime(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].verifyInRuntime(r, verbose)

def verifyFirmwareVersionRecentAs(v1, v2, v3, v4, target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].verifyFirmwareVersionRecentAs(v1, v2, v3, v4, r, verbose)

