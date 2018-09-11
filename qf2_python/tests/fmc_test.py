#!/bin/env python

import string, time, sys, argparse
import kintex_interface

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')

args = parser.parse_args()

# Start the class
x = kintex_interface.interface(args.target)

num_errors = 0

print('Initial I/O status:')
print('')
x.print_io_status()
print('')

raw_input('Press a key when ready...')

print
print 'Checking for shorts to FMC connectors...'

print
print 'TOP FMC LA P:'
print

for i in range(0, 34):
    x.set_top_fmc_la_p(1 << i, 0x3FFFFFFFF)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_top_fmc_la_p()),
    if ( x.get_top_fmc_la_p() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_top_fmc_la_p((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_top_fmc_la_p()),
    if ( x.get_top_fmc_la_p() != ((1 << i) ^ 0x3FFFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'TOP FMC LA N:'
print

for i in range(0, 34):
    x.set_top_fmc_la_n(1 << i, 0x3FFFFFFFF)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_top_fmc_la_n()),
    if ( x.get_top_fmc_la_n() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_top_fmc_la_n((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_top_fmc_la_n()),
    if ( x.get_top_fmc_la_n() != ((1 << i) ^ 0x3FFFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC LA P:'
print

for i in range(0, 34):
    x.set_bottom_fmc_la_p(1 << i, 0x3FFFFFFFF)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_bottom_fmc_la_p()),
    if ( x.get_bottom_fmc_la_p() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_la_p((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_bottom_fmc_la_p()),
    if ( x.get_bottom_fmc_la_p() != ((1 << i) ^ 0x3FFFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC LA N:'
print

for i in range(0, 34):
    x.set_bottom_fmc_la_n(1 << i, 0x3FFFFFFFF)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_bottom_fmc_la_n()),
    if ( x.get_bottom_fmc_la_n() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_la_n((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_bottom_fmc_la_n()),
    if ( x.get_bottom_fmc_la_n() != ((1 << i) ^ 0x3FFFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HA P:'
print

for i in range(0, 24):
    x.set_bottom_fmc_ha_p(1 << i, 0xFFFFFF)
    print '{0:024b}'.format(1 << i), '{0:024b}'.format(x.get_bottom_fmc_ha_p()),
    if ( x.get_bottom_fmc_ha_p() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_ha_p((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
    print '{0:024b}'.format((1 << i) ^ 0xFFFFFF), '{0:024b}'.format(x.get_bottom_fmc_ha_p()),
    if ( x.get_bottom_fmc_ha_p() != ((1 << i) ^ 0xFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HA N:'
print

for i in range(0, 24):
    x.set_bottom_fmc_ha_n(1 << i, 0xFFFFFF)
    print '{0:024b}'.format(1 << i), '{0:024b}'.format(x.get_bottom_fmc_ha_n()),
    if ( x.get_bottom_fmc_ha_n() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_ha_n((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
    print '{0:024b}'.format((1 << i) ^ 0xFFFFFF), '{0:024b}'.format(x.get_bottom_fmc_ha_n()),
    if ( x.get_bottom_fmc_ha_n() != ((1 << i) ^ 0xFFFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HB P:'
print

for i in range(0, 22):
    x.set_bottom_fmc_hb_p(1 << i, 0x3FFFFF)
    print '{0:022b}'.format(1 << i), '{0:022b}'.format(x.get_bottom_fmc_hb_p()),
    if ( x.get_bottom_fmc_hb_p() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_hb_p((1 << i) ^ 0x3FFFFF, 0x3FFFFF)
    print '{0:022b}'.format((1 << i) ^ 0x3FFFFF), '{0:022b}'.format(x.get_bottom_fmc_hb_p()),
    if ( x.get_bottom_fmc_hb_p() != ((1 << i) ^ 0x3FFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HB N:'
print

for i in range(0, 22):
    x.set_bottom_fmc_hb_n(1 << i, 0x3FFFFF)
    print '{0:022b}'.format(1 << i), '{0:022b}'.format(x.get_bottom_fmc_hb_n()),
    if ( x.get_bottom_fmc_hb_n() != 1 << i ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_hb_n((1 << i) ^ 0x3FFFFF, 0x3FFFFF)
    print '{0:022b}'.format((1 << i) ^ 0x3FFFFF), '{0:022b}'.format(x.get_bottom_fmc_hb_n()),
    if ( x.get_bottom_fmc_hb_n() != ((1 << i) ^ 0x3FFFFF) ):
        print ' ******** ',
        num_errors += 1
    print

print 'I/O scan complete, to continue, attach debug mezzanine to TOP FMC site'
raw_input('Press a key when ready...')

print
print 'TOP FMC LA P:'
print

for i in range(0, 10):
    x.set_top_fmc_la_p(1 << i, 1 << i)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_top_fmc_la_p()),
    if ( x.get_top_fmc_la_p() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_top_fmc_la_p(0, 1 << i)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_top_fmc_la_p()),
    if ( x.get_top_fmc_la_p() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'TOP FMC LA N:'
print

for i in range(0, 10):
    x.set_top_fmc_la_n(1 << i, 1 << i)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_top_fmc_la_n()),
    if ( x.get_top_fmc_la_n() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_top_fmc_la_n(0, 1 << i)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_top_fmc_la_n()),
    if ( x.get_top_fmc_la_n() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print 'I/O scan complete, to continue, attach debug mezzanine to BOTTOM FMC site'
raw_input('Press a key when ready...')

print
print 'BOTTOM FMC LA P:'
print

for i in range(0, 10):
    x.set_bottom_fmc_la_p(1 << i, 1 << i)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_bottom_fmc_la_p()),
    if ( x.get_bottom_fmc_la_p() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_la_p(0, 1 << i)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_bottom_fmc_la_p()),
    if ( x.get_bottom_fmc_la_p() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC LA N:'
print

for i in range(0, 10):
    x.set_bottom_fmc_la_n(1 << i, 1 << i)
    print '{0:034b}'.format(1 << i), '{0:034b}'.format(x.get_bottom_fmc_la_n()),
    if ( x.get_bottom_fmc_la_n() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_la_n(0, 1 << i)
    print '{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF), '{0:034b}'.format(x.get_bottom_fmc_la_n()),
    if ( x.get_bottom_fmc_la_n() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HA P:'
print

for i in range(0, 10):
    x.set_bottom_fmc_ha_p(1 << i, 1 << i)
    print '{0:024b}'.format(1 << i), '{0:024b}'.format(x.get_bottom_fmc_ha_p()),
    if ( x.get_bottom_fmc_ha_p() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_ha_p(0, 1 << i)
    print '{0:024b}'.format((1 << i) ^ 0xFFFFFF), '{0:024b}'.format(x.get_bottom_fmc_ha_p()),
    if ( x.get_bottom_fmc_ha_p() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HA N:'
print

for i in range(0, 10):
    x.set_bottom_fmc_ha_n(1 << i, 1 << i)
    print '{0:024b}'.format(1 << i), '{0:024b}'.format(x.get_bottom_fmc_ha_n()),
    if ( x.get_bottom_fmc_ha_n() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_ha_n(0, 1 << i)
    print '{0:024b}'.format((1 << i) ^ 0xFFFFFF), '{0:024b}'.format(x.get_bottom_fmc_ha_n()),
    if ( x.get_bottom_fmc_ha_n() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HB P:'
print

for i in range(0, 10):
    x.set_bottom_fmc_hb_p(1 << i, 1 << i)
    print '{0:022b}'.format(1 << i), '{0:022b}'.format(x.get_bottom_fmc_hb_p()),
    if ( x.get_bottom_fmc_hb_p() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_hb_p(0, 1 << i)
    print '{0:022b}'.format((1 << i) ^ 0x3FFFFF), '{0:022b}'.format(x.get_bottom_fmc_hb_p()),
    if ( x.get_bottom_fmc_hb_p() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print 'BOTTOM FMC HB N:'
print

for i in range(0, 10):
    x.set_bottom_fmc_hb_n(1 << i, 1 << i)
    print '{0:022b}'.format(1 << i), '{0:022b}'.format(x.get_bottom_fmc_hb_n()),
    if ( x.get_bottom_fmc_hb_n() & (1 << (i + 10)) == 0 ):
        print ' ******** ',
        num_errors += 1
    print
    x.set_bottom_fmc_hb_n(0, 1 << i)
    print '{0:022b}'.format((1 << i) ^ 0x3FFFFF), '{0:022b}'.format(x.get_bottom_fmc_hb_n()),
    if ( x.get_bottom_fmc_hb_n() & (1 << (i + 10)) != 0 ):
        print ' ******** ',
        num_errors += 1
    print

print
print('Number of errors: '+str(num_errors))
print
