#!/bin/env python

from socket import *
from datetime import datetime, timedelta
import string, argparse, time, sys

parser = argparse.ArgumentParser(description='Check board identification information', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
args = parser.parse_args()

UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.bind(("0.0.0.0", 0))
UDPSock.settimeout(0.2)

bytes = bytearray([0])
data = str(bytes)

UDPSock.sendto(data,(args.target,50000))
result = UDPSock.recv(1000)

r = bytearray(result)
r.reverse()

print
print 'Board ID packet format:', r[0]
if r[0] != 0:
        print 'ERROR - unrecognized board ID packet format'
        exit(1)

if r[1] == 0:
        print 'Board type: BMB7 r1'
elif r[1] == 1:
        print 'Board type: QF2-pre'
else:
        print 'ERROR - unrecognized board type'
        exit(1)

if r[2] == 0:
        print 'Active firmware: BOOTLOADER'
elif r[2] == 1:
        print 'Active firmware: RUNTIME'
else:
        print 'ERROR - unrecognized firmware mode'
        exit(1)

print

j = 0
for i in range(0, 8):
        j = j + (int(r[3+i]) << (i*8))
print 'Bootloader build timestamp:', j, '('+str(datetime.utcfromtimestamp(j))+')'
print 'Bootloader firmware SHA256:',
s = str()
x = r[11:43]
x.reverse()
for i in x: s += '{:02x}'.format(i)
print s
print

j = 0
for i in range(0, 8):
        j = j + (int(r[43+i]) << (i*8))
print 'Runtime build timestamp:', j, '('+str(datetime.utcfromtimestamp(j))+')'
print 'Runtime firmware SHA256:',
s = str()
x = r[51:83]
x.reverse()
for i in x: s += '{:02x}'.format(i)
print s
print

UDPSock.close()
