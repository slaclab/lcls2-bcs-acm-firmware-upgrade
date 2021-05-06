#!/usr/bin/env python

import argparse, sys
import qf2_python.identifier as identifier

# Compatibility layer
if sys.version_info < (3,):
    import qf2_python.compat.python2 as compat
else:
    import qf2_python.compat.python3 as compat

parser = argparse.ArgumentParser(description='Read QSFP data', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Only in the runtime
identifier.verifyInRuntime(args.target, args.verbose)

x = identifier.get_active_interface(args.target, args.verbose)

# This code will throw an I2C ack failure if the QSFP is not present
try:
    v = x.spartan_qsfp_get()
    for key, value in compat.dict_iteritems(v):
        print(key, ':', value)
except Exception as inst:
    if inst.args[0] == 'I2C acknowledge failed':
        print('Spartan QSFP doesn\'t appear to be present')
    else:
        raise inst

# This code will throw an I2C ack failure if the QSFP is not present
try:
    v = x.kintex_qsfp_1_get()
    for key, value in compat.dict_iteritems(v):
        print(key, ':', value)
except Exception as inst:
    if inst.args[0] == 'I2C acknowledge failed':
        print('Kintex QSFP 1 doesn\'t appear to be present')
    else:
        raise inst
    
# This code will throw an I2C ack failure if the QSFP is not present
try:
    v = x.kintex_qsfp_2_get()
    for key, value in compat.dict_iteritems(v):
        print(key, ':', value)
except Exception as inst:
    if inst.args[0] == 'I2C acknowledge failed':
        print('Kintex QSFP 2 doesn\'t appear to be present')
    else:
        raise inst


