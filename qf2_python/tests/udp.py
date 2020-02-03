#!/bin/env python

import argparse, time, sys, socket

# Compatibility layer
if sys.version_info < (3,):
    import qf2_python.compat.python2 as compat
else:
    import qf2_python.compat.python3 as compat

parser = argparse.ArgumentParser(description='Test UDP loopback', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-p', '--port', default='7', help='Target port')
args = parser.parse_args()

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
UDPSock.bind(("0.0.0.0", 0))
UDPSock.settimeout(2)

print('Targeting %s:%s' % (args.target, args.port))
print('\nStarting echo test.  Control-C to quit.')

totalbytes = 0
timestamp = time.time()
prevdonestamp = int(-1)

size = int(1450)
bytes = bytearray(size)

for i in range(0, size):
    bytes[i] = i & 0xFF

data = str(bytes)
data2 = str()

loopcount = 0

while True:
        
    size = size + 1
    if size == 1451:
        size = 1
        
    data = bytes[0:size]
    UDPSock.sendto(data,(args.target,int(args.port)))
    try:
        data2 = UDPSock.recv(size)
        if not data2:
            print('No data received')
            exit()
    except KeyboardInterrupt:
        print('Ctrl-C detected')
        exit()
    except:
        compat.print_no_flush('T')
        continue

    rbytes = bytearray(data2)
    if len(rbytes) != size:
        print('Incorrect data volume received - expected ' + str(size) + ' but received ' + str(len(rbytes)))
        exit()
        
    if bytes[0:size] != rbytes:
        print('Incorrect data received')
        exit()

    totalbytes += len(rbytes)
    donestamp = time.time()
    rate = totalbytes / (donestamp - timestamp) / 1024

    if int(prevdonestamp) != int(donestamp):
        print('')
        print('Rcvd: %s bytes, %s total in %s s at %s kB/s' % (len(data2), totalbytes, donestamp - timestamp, rate))
        prevdonestamp = donestamp
        
    time.sleep(0.01)

UDPSock.close()
