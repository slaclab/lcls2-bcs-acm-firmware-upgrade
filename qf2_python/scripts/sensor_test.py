#!/bin/env python

import argparse, ctypes
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre oscillator settings and check current frequency', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

# BME280 - Chain 0x2, address 0x76

# Put humidity in oversample x4
x.i2c_controller_write(2, 0x76, 0xF2, 0x3)

# Sample at 1s intervals, IIR filter off, SPI disabled
x.i2c_controller_write(2, 0x76, 0xF5, 0xA0)

# Put in normal sampling mode, x4 oversample of pressure and temperature
x.i2c_controller_write(2, 0x76, 0xF4, 0x6F)

# Read the calibration coefficients
coeffs = {
   'dig_T1' : x.i2c_controller_read(2, 0x76, 0x88, True),
   'dig_T2' : x.i2c_controller_read(2, 0x76, 0x8A, True),
   'dig_T3' : x.i2c_controller_read(2, 0x76, 0x8C, True),
   'dig_P1' : x.i2c_controller_read(2, 0x76, 0x8E, True),
   'dig_P2' : x.i2c_controller_read(2, 0x76, 0x90, True),
   'dig_P3' : x.i2c_controller_read(2, 0x76, 0x92, True),
   'dig_P4' : x.i2c_controller_read(2, 0x76, 0x94, True),
   'dig_P5' : x.i2c_controller_read(2, 0x76, 0x96, True),
   'dig_P6' : x.i2c_controller_read(2, 0x76, 0x98, True),
   'dig_P7' : x.i2c_controller_read(2, 0x76, 0x9A, True),
   'dig_P8' : x.i2c_controller_read(2, 0x76, 0x9C, True),
   'dig_P9' : x.i2c_controller_read(2, 0x76, 0x9E, True),
   'dig_H1' : x.i2c_controller_read(2, 0x76, 0xA1),
   'dig_H2' : x.i2c_controller_read(2, 0x76, 0xE1, True),
   'dig_H3' : x.i2c_controller_read(2, 0x76, 0xE3),
   'dig_H4' : (x.i2c_controller_read(2, 0x76, 0xE4) << 4) | (x.i2c_controller_read(2, 0x76, 0xE5) & 0xF),
   'dig_H5' : (x.i2c_controller_read(2, 0x76, 0xE6) << 4) | (x.i2c_controller_read(2, 0x76, 0xE5) >> 4),
   'dig_H6' : ctypes.c_byte(x.i2c_controller_read(2, 0x76, 0xE7)).value,
   }

# Switch around the reverse coefficients
coeffs['dig_T1'] = ((coeffs['dig_T1'] & 0xFF) << 8) | (coeffs['dig_T1'] >> 8)
coeffs['dig_T2'] = ctypes.c_short(((coeffs['dig_T2'] & 0xFF) << 8) | (coeffs['dig_T2'] >> 8)).value
coeffs['dig_T3'] = ctypes.c_short(((coeffs['dig_T3'] & 0xFF) << 8) | (coeffs['dig_T3'] >> 8)).value
coeffs['dig_P1'] = ((coeffs['dig_P1'] & 0xFF) << 8) | (coeffs['dig_P1'] >> 8)
coeffs['dig_P2'] = ctypes.c_short(((coeffs['dig_P2'] & 0xFF) << 8) | (coeffs['dig_P2'] >> 8)).value
coeffs['dig_P3'] = ctypes.c_short(((coeffs['dig_P3'] & 0xFF) << 8) | (coeffs['dig_P3'] >> 8)).value
coeffs['dig_P4'] = ctypes.c_short(((coeffs['dig_P4'] & 0xFF) << 8) | (coeffs['dig_P4'] >> 8)).value
coeffs['dig_P5'] = ctypes.c_short(((coeffs['dig_P5'] & 0xFF) << 8) | (coeffs['dig_P5'] >> 8)).value
coeffs['dig_P6'] = ctypes.c_short(((coeffs['dig_P6'] & 0xFF) << 8) | (coeffs['dig_P6'] >> 8)).value
coeffs['dig_P7'] = ctypes.c_short(((coeffs['dig_P7'] & 0xFF) << 8) | (coeffs['dig_P7'] >> 8)).value
coeffs['dig_P8'] = ctypes.c_short(((coeffs['dig_P8'] & 0xFF) << 8) | (coeffs['dig_P8'] >> 8)).value
coeffs['dig_P9'] = ctypes.c_short(((coeffs['dig_P9'] & 0xFF) << 8) | (coeffs['dig_P9'] >> 8)).value
coeffs['dig_H2'] = ctypes.c_short(((coeffs['dig_H2'] & 0xFF) << 8) | (coeffs['dig_H2'] >> 8)).value

#for i, j in sorted(coeffs.items()):
#   print i, j

# Temperature
temperature = x.i2c_controller_read(2, 0x76, 0xFA, True) << 4

v1 = ((float(temperature) / 16384.0) - (float(coeffs['dig_T1']) / 1024.0)) * float(coeffs['dig_T2'])
v2 = ((float(temperature) / 131072.0) - (float(coeffs['dig_T1']) / 8192.0))
v2 = v2 * v2 * float(coeffs['dig_T3'])
temperature = v1 + v2

# Print temperature
print 'Temperature: '+'{0:.2f}'.format(temperature / 5120.0)+' C'

# Humidity
humidity = x.i2c_controller_read(2, 0x76, 0xFD, True)

vh = temperature - 76800.0
vh = (float(humidity) - (float(coeffs['dig_H4']) * 64.0 + float(coeffs['dig_H5']) / 16384.0 * vh)) * (float(coeffs['dig_H2']) / 65536.0 * (1.0 + float(coeffs['dig_H6']) / 67108864.0 * vh * (1.0 + float(coeffs['dig_H3']) / 67108864.0 * vh)))
vh = vh * (1.0 - float(coeffs['dig_H1']) * vh / 524288.0)

if vh > 100.0:
   vh = 100.0
elif vh < 0.0:
   vh = 0.0

print 'Relative humidity: '+'{0:.2f}'.format(vh)+' %'

# Pressure
pressure = x.i2c_controller_read(2, 0x76, 0xF7, True) << 4

v1 = (temperature / 2.0) - 64000.0
v2 = v1 * v1 * float(coeffs['dig_P6']) / 32768.0
v2 = v2 + v1 * float(coeffs['dig_P5']) * 2.0
v2 = (v2 / 4.0) + (float(coeffs['dig_P4']) * 65536.0)
v1 = (float(coeffs['dig_P3']) * v1 * v1 / 524288.0 + float(coeffs['dig_P2']) * v1) / 524288.0
v1 = (1.0 + v1 / 32768.0) * float(coeffs['dig_P1'])
if (v1 == 0.0):
   print 'Pressure: 0.0 hPa'
   exit()

p = 1048576.0 - pressure
p = (p - (v2 / 4096.0)) * 6250.0 / v1
v1 = float(coeffs['dig_P9']) * p * p / 2147483648.0
v2 = p * float(coeffs['dig_P8']) / 32768.0
p = p + (v1 + v2 + float(coeffs['dig_P7'])) / 16.0
print 'Pressure: '+'{0:.2f}'.format(p/100.0)+' hPa'

# BMX055 accelerometer - Chain 0x2, address 0x18



x.i2c_controller_read(2, 0x18, 0x0)



# BMX055 gyro - chain 0x2, address 0x68








# BMX055 magnetometer - Chain 0x2, address 0x10
