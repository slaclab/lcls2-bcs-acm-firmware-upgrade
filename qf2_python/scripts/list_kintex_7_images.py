
#!/usr/bin/env python

import time, sys, argparse
from datetime import datetime
from qf2_python.configuration.jtag import *
from qf2_python.configuration.spi import *

SEQUENCER_PORT = 50003

parser = argparse.ArgumentParser(description='List available Kintex-7 boot images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')

args = parser.parse_args()

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# Create a Kintex firmware interface
interface = kintex_7_firmware.interface(prom)

# List the images in the firmware
images = interface.get_images()

if len(images) == 0:
    print 'No images stored'
    exit()

for i in images:

    print

    print 'SHA256:',
    s = str()
    for j in i['sha256']:
        s += '{:02x}'.format(j)
    print s

    print 'Bitstream address:', i['address']
    print 'Bitstream length (bits):', i['length'] * 8
    print 'Firmware build date:', i['build_date'], '(' + str(datetime.utcfromtimestamp(i['build_date'])) + ')'
    print 'Firmware storage date:', i['storage_date'], '(' + str(datetime.utcfromtimestamp(i['storage_date'])) + ')'

print
