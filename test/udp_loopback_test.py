#!/bin/env python

from socket import *
import string
import time, sys

# REMEMBER TO SPECIFY THE PROPER DETINATION HOST HERE...
# 'host' should be the address that the server half of this is running on
host = "192.168.1.127"

# if you change the port, change it on the server side as well
port = 50000

UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.bind(("0.0.0.0", 50002))
UDPSock.settimeout(0.2)

print "\nStarting echo test.  Control-C to quit."

print "\nOur target:"
print "echo server running on %s port %s" % (host, port)

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

while (1):
	UDPSock.sendto(data,(host,port))
	try:
                data2 = UDPSock.recv(size)
                if not data2:
                        print "No data received"
                        break
        except KeyboardInterrupt:
                print 'Ctrl-C detected'
                exit(0)
        except:
                print 'T',
                continue

	rbytes = bytearray(data2)
	if ( len(rbytes) != size ):
		print "Incorrect data volume received"
		break

	if ( bytes != rbytes ):
		print "Incorrect data received"
		break

	totalbytes += len(rbytes)
	donestamp = time.time()
	rate = totalbytes / (donestamp - timestamp) / 1024

	#for i in range(0, size):
	#	print bytes[i], rbytes[i]

	if int(prevdonestamp) != int(donestamp):
                print
		print "Rcvd: %s bytes, %s total in %s s at %s kB/s" % (len(data2), totalbytes, donestamp - timestamp, rate)
		prevdonestamp = donestamp

UDPSock.close()
