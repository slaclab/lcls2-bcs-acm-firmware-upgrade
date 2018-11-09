#!/bin/env python

import argparse
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre oscillator settings and check current frequency', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-p', '--part', default='SI57X_A', help='Target oscillator')
parser.add_argument('-r', '--rfreq', default=None, help='RFREQ setting')
parser.add_argument('-n', '--n', default=None, help='N1 setting')
parser.add_argument('-d', '--div', default=None, help='HSDIV setting')
parser.add_argument('-o', '--output_enable', action="store_true", help='Output enable')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

if args.part == 'SI57X_A':

   # Retrieve default settings
   r = x.si57X_a_get_defaults()

   if args.rfreq != None:
      r['RFREQ'] = int(args.rfreq, 0)
   if args.n != None:
      r['N1'] = int(args.n, 0)
   if args.div != None:
      r['HSDIV'] = int(args.div, 0)

   print('Changing SI57X_A register settings to:\n')

   print('RFREQ:\t'+str(hex(r['RFREQ'])))
   print('N1:\t'+str((r['N1'])))
   print('HSDIV:\t'+str((r['HSDIV'])))
   print('')

   x.si57X_a_set(r)

   if args.output_enable == True:
      print('Enabling output')
      x.si57X_a_enable()
   else:
      print('Disabling output')
      x.si57X_a_disable()

elif args.part == 'SI57X_B':

   # Retrieve default settings
   r = x.si57X_b_get_defaults()

   if args.rfreq != None:
      r['RFREQ'] = int(args.rfreq, 0)
   if args.n != None:
      r['N1'] = int(args.n, 0)
   if args.div != None:
      r['HSDIV'] = int(args.div, 0)

   print('Changing SI57X_B register settings to:\n')

   print('RFREQ:\t'+str(hex(r['RFREQ'])))
   print('N1:\t'+str((r['N1'])))
   print('HSDIV:\t'+str((r['HSDIV'])))
   print('')

   x.si57X_b_set(r)

   if args.output_enable == True:
      print('Enabling output')
      x.si57X_b_enable()
   else:
      print('Disabling output')
      x.si57X_b_disable()

else:
      raise Exception('Part unknown - '+str(args.part))
