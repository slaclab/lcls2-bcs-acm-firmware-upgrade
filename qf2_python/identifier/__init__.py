#!/usr/bin/env python

__all__ = [
    'interface',
    'v0',
    ]

import socket

HIGHEST_VERSION = 1

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
    x = ldict['x'].reboot_to_runtime(target, verbose)

    # Return the instance
    return x

def reboot_to_bootloader(target, verbose=False):
    # Query the board
    r = __query_board(target, verbose)
    
    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].reboot_to_bootloader(target, verbose)

    # Return the instance
    return x

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
