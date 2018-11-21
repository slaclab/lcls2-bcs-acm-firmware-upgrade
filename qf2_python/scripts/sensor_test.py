#!/bin/env python

import argparse, ctypes, time
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

# BMX055 accelerometer - Chain 0x2, address 0x18
   
# Set accel range +/- 2g
x.i2c_controller_write(2, 0x18, 0x0F, 0x03)
# Set BW register 7.81 Hz
x.i2c_controller_write(2, 0x18, 0x10, 0x08)
# Set mode == normal, sleep duration 0.5ms
x.i2c_controller_write(2, 0x18, 0x11, 0x00)

# BMX055 gyro - Chain 0x2, address 0x68
   
# Set range full scale +/- 125 degrees
x.i2c_controller_write(2, 0x68, 0x0F, 0x04)
# Set BW register 100Hz
x.i2c_controller_write(2, 0x68, 0x10, 0x07)
# Set mode == normal, sleep duration 2ms
x.i2c_controller_write(2, 0x68, 0x11, 0x00)

# BMX055 magnetometer - Chain 0x2, address 0x10

try:
   # Soft reset
   x.i2c_controller_write(2, 0x10, 0x4B, 0x83)
except:
   pass

# Normal mode, ODR 10Hz
x.i2c_controller_write(2, 0x10, 0x4C, 0x00)
# X, Y, Z enabled
x.i2c_controller_write(2, 0x10, 0x4E, 0x84)
# 9 repetitions for X & Y axes
x.i2c_controller_write(2, 0x10, 0x51, 0x04)
# 15 repetitions for Z axis
x.i2c_controller_write(2, 0x10, 0x52, 0x0F)

while True:

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

   # Could use Magwick / Mayhony filter below to improve result in dynamic applications...

   # BMX055 accelerometer - Chain 0x2, address 0x18
   
   xacc = x.i2c_controller_read(2, 0x18, 0x02, True)
   yacc = x.i2c_controller_read(2, 0x18, 0x04, True)
   zacc = x.i2c_controller_read(2, 0x18, 0x06, True)

   xacc = (xacc >> 12) | ((xacc & 0xFF) << 4)
   yacc = (yacc >> 12) | ((yacc & 0xFF) << 4)
   zacc = (zacc >> 12) | ((zacc & 0xFF) << 4)

   if xacc > 2047:
      xacc -= 4096
   if yacc > 2047:
      yacc -= 4096
   if zacc > 2047:
      zacc -= 4096

   xacc = float(xacc) * (2.0 / 2047.0)
   yacc = float(yacc) * (2.0 / 2047.0)
   zacc = float(zacc) * (2.0 / 2047.0)

   print 'Accelerometer X:', '{0:.2f}'.format(xacc), ' g'
   print 'Accelerometer Y:', '{0:.2f}'.format(yacc), ' g'
   print 'Accelerometer Z:', '{0:.2f}'.format(zacc), ' g'

   # BMX055 gyro - Chain 0x2, address 0x68

   xgyr = x.i2c_controller_read(2, 0x68, 0x02, True)
   ygyr = x.i2c_controller_read(2, 0x68, 0x04, True)
   zgyr = x.i2c_controller_read(2, 0x68, 0x06, True)

   xgyr = (xgyr >> 8) | ((xgyr & 0xFF) << 8)
   ygyr = (ygyr >> 8) | ((ygyr & 0xFF) << 8)
   zgyr = (zgyr >> 8) | ((zgyr & 0xFF) << 8)

   if xgyr > 32767:
      xgyr -= 65536
   if ygyr > 32767:
      ygyr -= 65536
   if zgyr > 32767:
      zgyr -= 65536

   # Doesn't seem to quite match the '262.4 LSB/deg/s' in the manual
   xgyr = float(xgyr) * (125.0 / 32767.0)
   ygyr = float(ygyr) * (125.0 / 32767.0)
   zgyr = float(zgyr) * (125.0 / 32767.0)

   print 'Gyro X:', '{0:.2f}'.format(xgyr), ' degrees'
   print 'Gyro Y:', '{0:.2f}'.format(ygyr), ' degrees'
   print 'Gyro Z:', '{0:.2f}'.format(zgyr), ' degrees'
   
   # BMX055 magnetometer - Chain 0x2, address 0x10
   # Can temperature compensate using RHALL... TBD

   xmag = x.i2c_controller_read(2, 0x10, 0x42, True)
   ymag = x.i2c_controller_read(2, 0x10, 0x44, True)
   zmag = x.i2c_controller_read(2, 0x10, 0x46, True)
   rhall = x.i2c_controller_read(2, 0x10, 0x48, True)

   xmag = (xmag >> 11) | ((xmag & 0xFF) << 5)
   ymag = (ymag >> 11) | ((ymag & 0xFF) << 5)
   zmag = (zmag >> 9) | ((zmag & 0xFF) << 7)
   rhall = (rhall >> 10) | ((rhall & 0xFF) << 6)

   if xmag > 4095:
      xmag -= 8192
   if ymag > 4096:
      ymag -= 8192
   if zmag > 16383:
      zmag -= 32768

   # Rough calibration for testing purposes
   xmag = float(xmag) * 0.3
   ymag = float(ymag) * 0.3
   zmag = float(zmag) * 0.3

   print 'Mag X:', '{0:.2f}'.format(xmag), ' uT'
   print 'Mag Y:', '{0:.2f}'.format(ymag), ' uT'
   print 'Mag Z:', '{0:.2f}'.format(zmag), ' uT'

   print('')
   time.sleep(0.5)









