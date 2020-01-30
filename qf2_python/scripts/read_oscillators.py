#!/bin/env python

import argparse
import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Display QF2-pre oscillator settings and check current frequency', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Only in the runtime
identifier.verifyInRuntime(args.target, args.verbose)

# Start the class
x = identifier.get_active_interface(args.target, args.verbose)

if x.si57X_a_is_enabled():
   print('SI57X_A output is enabled, approximate frequency:\t'+'{0:0.3f}'.format(x.si57X_a_frequency() / 1000000.0) + 'MHz')
else:
   print('SI57X_A output is currently disabled - frequency measurement unavailable')

if x.si57X_b_is_enabled():
   print('SI57X_B output is enabled, approximate frequency:\t'+'{0:0.3f}'.format(x.si57X_b_frequency() / 1000000.0) + 'MHz')
else:
   print('SI57X_B output is currently disabled - frequency measurement unavailable')

