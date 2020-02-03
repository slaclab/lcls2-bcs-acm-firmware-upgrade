#!/bin/env python

import argparse
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre oscillator settings and check current frequency', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-p', '--part', default='SI57X_A', help='Target oscillator')
parser.add_argument('-f', '--frequency', type=float, required=True, help='New frequency')
parser.add_argument('-d', '--default', type=float, default=156.25, help='Default frequency')
parser.add_argument('-o', '--output_enable', default=False, action="store_true", help='Output enable')
parser.add_argument('-v', '--verbose', default=False, action="store_true", help='Verbose output')
args = parser.parse_args()

print('\nNOTE: This code assumes the startup frequency of the SI570 is 156.25MHz. If you are using a non-standard part you will needed to override it (-d).\n')

def compute(r):

   print('RFREQ:\t'+str(hex(r['RFREQ'])))
   print('N1:\t'+str((r['N1'])))
   print('HSDIV:\t'+str((r['HSDIV'])))

   fxtal = (args.default * (r['N1']+1) * (r['HSDIV']+4)) / (float(r['RFREQ']) / 2**28)
   fdco = args.default * (r['N1']+1) * (r['HSDIV']+4)

   print('=> Crystal frequency: '+str(fxtal)+'MHz')
   print('=> DCO frequency: '+str(fdco)+'MHz')
   print('')

   # DCO frequency range: 4850 - 5670MHz
   # HSDIV values: 4, 5, 6, 7, 9 or 11 (subtract 4 to store)
   # N1 values: 1, 2, 4, 6, 8...128

   print('Possible settings are:\n')

   # Find the lowest acceptable DCO value (lowest power)
   best = [0, 0, 6000.0]
   for i in range(0, 65):
      n1 = i*2
      if i == 0:
         n1 = 1
      for hsdiv in [4, 5, 6, 7, 9, 11]:
         fdco = args.frequency * n1 * hsdiv
         if (fdco > 4850.0) and (fdco < 5670.0):
            print(n1-1, hsdiv-4, fdco)
            if fdco < best[2]:
               best = [n1, hsdiv, fdco]

   if best[2] > 5700.0:
      raise Exception('Could not find appropriate settings for your target frequency')

   print('\nBest option is:\n')
   print(best[0]-1, best[1]-4, best[2])

   r['N1'] = best[0]-1
   r['HSDIV'] = best[1]-4
   r['RFREQ'] = int(best[2] * float(2**28) / fxtal)

   return r

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

if args.part == 'SI57X_A':

   # Retrieve default settings
   r = x.si57X_a_get_defaults()

   print('Default SI57X_A register settings are:\n')

   r = compute(r)
   
   print('\nChanging SI57X_A register settings to:\n')

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

   print('Default SI57X_B register settings are:\n')

   r = compute(r)
   
   print('\nChanging SI57X_B register settings to:\n')

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
