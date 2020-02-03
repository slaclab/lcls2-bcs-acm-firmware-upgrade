#!/bin/env python

import sys

# Compatibility layer
if sys.version_info < (3,):
    import qf2_python.compat.python2 as compat
else:
    import qf2_python.compat.python3 as compat

def test_mfc_full_with_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on loopback mounted full MFC:')

    print('')
    print('P:')
    print('')

    for i in range(0, 12):
        x.set_full_mfc_p(1 << i, 1 << i)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_full_mfc_p()))
        if ( x.get_full_mfc_p() & (1 << (i + 12)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_full_mfc_p(0, 1 << i)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_full_mfc_p()))
        if ( x.get_full_mfc_p() & (1 << (i + 12)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('N:')
    print('')

    for i in range(0, 12):
        x.set_full_mfc_n(1 << i, 1 << i)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_full_mfc_n()))
        if ( x.get_full_mfc_n() & (1 << (i + 12)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_full_mfc_n(0, 1 << i)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_full_mfc_n()))
        if ( x.get_full_mfc_n() & (1 << (i + 12)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_mfc_aux_with_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on loopback mounted auxilliary MFC:')
    print('')
    print('P:')
    print('')

    for i in range(0, 8):
        x.set_aux_mfc_p(1 << i, 1 << i)
        compat.print_no_flush('{0:020b}'.format(1 << i) + ' {0:020b}'.format(x.get_aux_mfc_p()))
        if ( x.get_aux_mfc_p() & (1 << (i + 12)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_aux_mfc_p(0, 1 << i)
        compat.print_no_flush('{0:020b}'.format((1 << i) ^ 0xFFFFF) + ' {0:020b}'.format(x.get_aux_mfc_p()))
        if ( x.get_aux_mfc_p() & (1 << (i + 12)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('N:')
    print('')

    for i in range(0, 8):
        x.set_aux_mfc_n(1 << i, 1 << i)
        compat.print_no_flush('{0:020b}'.format(1 << i) + ' {0:020b}'.format(x.get_aux_mfc_n()))
        if ( x.get_aux_mfc_n() & (1 << (i + 12)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_aux_mfc_n(0, 1 << i)
        compat.print_no_flush('{0:020b}'.format((1 << i) ^ 0xFFFFF) + ' {0:020b}'.format(x.get_aux_mfc_n()))
        if ( x.get_aux_mfc_n() & (1 << (i + 12)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_fmc_top_with_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on loopback mounted top FMC:')
    print('')
    print('LA P:')
    print('')

    for i in range(0, 10):
        x.set_top_fmc_la_p(1 << i, 1 << i)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_top_fmc_la_p()))
        if ( x.get_top_fmc_la_p() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_top_fmc_la_p(0, 1 << i)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) +  ' {0:034b}'.format(x.get_top_fmc_la_p()))
        if ( x.get_top_fmc_la_p() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('LA N:')
    print('')

    for i in range(0, 10):
        x.set_top_fmc_la_n(1 << i, 1 << i)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_top_fmc_la_n()))
        if ( x.get_top_fmc_la_n() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_top_fmc_la_n(0, 1 << i)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_top_fmc_la_n()))
        if ( x.get_top_fmc_la_n() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_fmc_bottom_with_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on loopback mounted bottom FMC:')
    print('')
    print('LA P:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_la_p(1 << i, 1 << i)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_bottom_fmc_la_p()))
        if ( x.get_bottom_fmc_la_p() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_la_p(0, 1 << i)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_bottom_fmc_la_p()))
        if ( x.get_bottom_fmc_la_p() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('LA N:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_la_n(1 << i, 1 << i)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_bottom_fmc_la_n()))
        if ( x.get_bottom_fmc_la_n() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_la_n(0, 1 << i)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_bottom_fmc_la_n()))
        if ( x.get_bottom_fmc_la_n() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HA P:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_ha_p(1 << i, 1 << i)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_bottom_fmc_ha_p()))
        if ( x.get_bottom_fmc_ha_p() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_ha_p(0, 1 << i)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_bottom_fmc_ha_p()))
        if ( x.get_bottom_fmc_ha_p() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HA N:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_ha_n(1 << i, 1 << i)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_bottom_fmc_ha_n()))
        if ( x.get_bottom_fmc_ha_n() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_ha_n(0, 1 << i)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_bottom_fmc_ha_n()))
        if ( x.get_bottom_fmc_ha_n() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HB P:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_hb_p(1 << i, 1 << i)
        compat.print_no_flush('{0:022b}'.format(1 << i) + ' {0:022b}'.format(x.get_bottom_fmc_hb_p()))
        if ( x.get_bottom_fmc_hb_p() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_hb_p(0, 1 << i)
        compat.print_no_flush('{0:022b}'.format((1 << i) ^ 0x3FFFFF) + ' {0:022b}'.format(x.get_bottom_fmc_hb_p()))
        if ( x.get_bottom_fmc_hb_p() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HB N:')
    print('')

    for i in range(0, 10):
        x.set_bottom_fmc_hb_n(1 << i, 1 << i)
        compat.print_no_flush('{0:022b}'.format(1 << i) + ' {0:022b}'.format(x.get_bottom_fmc_hb_n()))
        if ( x.get_bottom_fmc_hb_n() & (1 << (i + 10)) == 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_hb_n(0, 1 << i)
        compat.print_no_flush('{0:022b}'.format((1 << i) ^ 0x3FFFFF) + ' {0:022b}'.format(x.get_bottom_fmc_hb_n()))
        if ( x.get_bottom_fmc_hb_n() & (1 << (i + 10)) != 0 ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_fmc_top_no_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on unmounted top FMC:')
    print('')
    print('LA P:')
    print('')

    for i in range(0, 34):
        x.set_top_fmc_la_p(1 << i, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_top_fmc_la_p()))
        if ( x.get_top_fmc_la_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_top_fmc_la_p((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_top_fmc_la_p()))
        if ( x.get_top_fmc_la_p() != ((1 << i) ^ 0x3FFFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('LA N:')
    print('')

    for i in range(0, 34):
        x.set_top_fmc_la_n(1 << i, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_top_fmc_la_n()))
        if ( x.get_top_fmc_la_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_top_fmc_la_n((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_top_fmc_la_n()))
        if ( x.get_top_fmc_la_n() != ((1 << i) ^ 0x3FFFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_fmc_bottom_no_loopback():

    num_errors = 0

    print('')
    print('Checking I/O on unmounted bottom FMC:')
    print('')
    print('LA P:')
    print('')

    for i in range(0, 34):
        x.set_bottom_fmc_la_p(1 << i, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_bottom_fmc_la_p()))
        if ( x.get_bottom_fmc_la_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_la_p((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_bottom_fmc_la_p()))
        if ( x.get_bottom_fmc_la_p() != ((1 << i) ^ 0x3FFFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('LA N:')
    print('')

    for i in range(0, 34):
        x.set_bottom_fmc_la_n(1 << i, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format(1 << i) + ' {0:034b}'.format(x.get_bottom_fmc_la_n()))
        if ( x.get_bottom_fmc_la_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_la_n((1 << i) ^ 0x3FFFFFFFF, 0x3FFFFFFFF)
        compat.print_no_flush('{0:034b}'.format((1 << i) ^ 0x3FFFFFFFF) + ' {0:034b}'.format(x.get_bottom_fmc_la_n()))
        if ( x.get_bottom_fmc_la_n() != ((1 << i) ^ 0x3FFFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HA P:')
    print('')

    for i in range(0, 24):
        x.set_bottom_fmc_ha_p(1 << i, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_bottom_fmc_ha_p()))
        if ( x.get_bottom_fmc_ha_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_ha_p((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_bottom_fmc_ha_p()))
        if ( x.get_bottom_fmc_ha_p() != ((1 << i) ^ 0xFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HA N:')
    print('')

    for i in range(0, 24):
        x.set_bottom_fmc_ha_n(1 << i, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_bottom_fmc_ha_n()))
        if ( x.get_bottom_fmc_ha_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_ha_n((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_bottom_fmc_ha_n()))
        if ( x.get_bottom_fmc_ha_n() != ((1 << i) ^ 0xFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HB P:')
    print('')

    for i in range(0, 22):
        x.set_bottom_fmc_hb_p(1 << i, 0x3FFFFF)
        compat.print_no_flush('{0:022b}'.format(1 << i) + ' {0:022b}'.format(x.get_bottom_fmc_hb_p()))
        if ( x.get_bottom_fmc_hb_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_hb_p((1 << i) ^ 0x3FFFFF, 0x3FFFFF)
        compat.print_no_flush('{0:022b}'.format((1 << i) ^ 0x3FFFFF) + ' {0:022b}'.format(x.get_bottom_fmc_hb_p()))
        if ( x.get_bottom_fmc_hb_p() != ((1 << i) ^ 0x3FFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('HB N:')
    print('')

    for i in range(0, 22):
        x.set_bottom_fmc_hb_n(1 << i, 0x3FFFFF)
        compat.print_no_flush('{0:022b}'.format(1 << i) + ' {0:022b}'.format(x.get_bottom_fmc_hb_n()))
        if ( x.get_bottom_fmc_hb_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_bottom_fmc_hb_n((1 << i) ^ 0x3FFFFF, 0x3FFFFF)
        compat.print_no_flush('{0:022b}'.format((1 << i) ^ 0x3FFFFF) + ' {0:022b}'.format(x.get_bottom_fmc_hb_n()))
        if ( x.get_bottom_fmc_hb_n() != ((1 << i) ^ 0x3FFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_mfc_full_no_loopback():

    num_errors = 0
    
    print('')
    print('Checking I/O on unmounted full MFC:')
    print('')
    print('P:')
    print('')

    for i in range(0, 24):
        x.set_full_mfc_p(1 << i, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_full_mfc_p()))
        if ( x.get_full_mfc_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_full_mfc_p((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_full_mfc_p()))
        if ( x.get_full_mfc_p() != ((1 << i) ^ 0xFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('N:')
    print('')

    for i in range(0, 24):
        x.set_full_mfc_n(1 << i, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format(1 << i) + ' {0:024b}'.format(x.get_full_mfc_n()))
        if ( x.get_full_mfc_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_full_mfc_n((1 << i) ^ 0xFFFFFF, 0xFFFFFF)
        compat.print_no_flush('{0:024b}'.format((1 << i) ^ 0xFFFFFF) + ' {0:024b}'.format(x.get_full_mfc_n()))
        if ( x.get_full_mfc_n() != ((1 << i) ^ 0xFFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

def test_mfc_aux_no_loopback():

    num_errors = 0
 
    print('')
    print('Checking I/O on unmounted auxilliary MFC:')
    print('')
    print('P:')
    print('')

    for i in range(0, 20):
        x.set_aux_mfc_p(1 << i, 0xFFFFF)
        compat.print_no_flush('{0:020b}'.format(1 << i) + ' {0:020b}'.format(x.get_aux_mfc_p()))
        if ( x.get_aux_mfc_p() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_aux_mfc_p((1 << i) ^ 0xFFFFF, 0xFFFFF)
        compat.print_no_flush('{0:020b}'.format((1 << i) ^ 0xFFFFF) + ' {0:020b}'.format(x.get_aux_mfc_p()))
        if ( x.get_aux_mfc_p() != ((1 << i) ^ 0xFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    print('')
    print('N:')
    print('')

    for i in range(0, 20):
        x.set_aux_mfc_n(1 << i, 0xFFFFF)
        compat.print_no_flush('{0:020b}'.format(1 << i) + ' {0:020b}'.format(x.get_aux_mfc_n()))
        if ( x.get_aux_mfc_n() != 1 << i ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')
        x.set_aux_mfc_n((1 << i) ^ 0xFFFFF, 0xFFFFF)
        compat.print_no_flush('{0:020b}'.format((1 << i) ^ 0xFFFFF) + ' {0:020b}'.format(x.get_aux_mfc_n()))
        if ( x.get_aux_mfc_n() != ((1 << i) ^ 0xFFFFF) ):
            compat.print_no_flush(' ******** ')
            num_errors += 1
        print('')

    return num_errors

import string, time, argparse

import qf2_python.identifier as identifier
import qf2_python.tests.kintex_interface as kintex_interface

parser = argparse.ArgumentParser(description='Test mezzanine interfaces', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')
parser.add_argument('-ma', '--mfc_aux', action="store_true", default=False, help='Test auxilliary MFC')
parser.add_argument('-mf', '--mfc_full', action="store_true", default=False, help='Test full MFC')
parser.add_argument('-ft', '--fmc_top', action='store_true', default=False, help='Test top FMC')
parser.add_argument('-fb', '--fmc_bottom', action='store_true', default=False, help='Test bottom FMC')
parser.add_argument('-l', '--loopback', action="store_true", default=False, help='Loopbacks are mounted')
parser.add_argument('-p', '--pause', action="store_true", default=False, help='Pause (wait for keypress) before testing')

args = parser.parse_args()

# Ensure we are in runtime
identifier.verifyInRuntime(args.target)

total_errors = 0

# Start the class
x = kintex_interface.interface(args.target)

print('Initial I/O status:')
print('')
x.print_io_status()
print('')

if args.pause == True:
    compat.my_raw_input('Press a key when ready...')

if args.loopback == True:
    if args.mfc_full == True:
        total_errors += test_mfc_full_with_loopback()
    if args.mfc_aux == True:
        total_errors += test_mfc_aux_with_loopback()
    if args.fmc_top == True:
        total_errors += test_fmc_top_with_loopback()
    if args.fmc_bottom == True:
        total_errors += test_fmc_bottom_with_loopback()
else:
    if args.mfc_full == True:
        total_errors += test_mfc_full_no_loopback()
    if args.mfc_aux == True:
        total_errors += test_mfc_aux_no_loopback()
    if args.fmc_top == True:
        total_errors += test_fmc_top_no_loopback()
    if args.fmc_bottom == True:
        total_errors += test_fmc_bottom_no_loopback()

print('')
print('Number of errors: '+str(total_errors))
print('')

exit(total_errors)







