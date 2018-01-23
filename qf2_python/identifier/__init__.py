#!/usr/bin/env python

__all__ = [
    'interface',
    'v0',
    ]

import socket

HIGHEST_VERSION = 0

def get_interface(target, verbose):
    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPSock.bind(("0.0.0.0", 0))
    UDPSock.settimeout(1)

    bytes = bytearray([0])
    #data = str(bytes)

    UDPSock.sendto(bytes,(target,50000))
    result = UDPSock.recv(1000)
    UDPSock.close()

    r = bytearray(result)
    r.reverse()

    if verbose == True:
        print('')
        print('Board ID packet format: '+str(r[0]))
        if r[0] > HIGHEST_VERSION:
            raise Exception('ERROR - unrecognized board ID packet format (', r[0], ')')

    # Decide on packet version interface to use and import the associated module
    ldict = locals()
    exec('import qf2_python.identifier.v'+str(r[0])+' as x')
    x = ldict['x'].get_interface(target, r, verbose)

    # Return the instance of the board interface
    return x
