#!/bin/env python

from math import *

import argparse, time, ctypes
import qf2_python.identifier
#import argparse, time, datetime

parser = argparse.ArgumentParser(description='Test microphone', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-f', '--file', default='mic_demo.wav', help='Output file name for recorded audio')
parser.add_argument('-l', '--length', default=5, type=int, help='Length of recording')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

print('Initializing audio subsystem...')
x.tas2505_enable()

# Assert software reset
x.tas2505_write(1, 1)
time.sleep(0.01) # Wait 10 ms

# Write the configuration coefficients for 44.1kHz operation from a 16MHz reference

x.tas2505_write(0, 1)
# LDO output programmed as 1.8V and level shifters powered up
x.tas2505_write(2, 0x4) # TODO: OR 0?

x.tas2505_write(0, 0)
# Pll_clkin = MCLK, codec_clkin = PLL_CLK, MCLK should be 16MHz
x.tas2505_write(4, 0x3)
# Power up PLL, P=1, R=1
x.tas2505_write(5, 0x91)
# J=5
x.tas2505_write(6, 0x5)
# D(13:8) = 0xB, D = 2920
x.tas2505_write(7, 0x0B)
# D(7:0) = 0x68
x.tas2505_write(8, 0x68)
# Wait 15ms for PLL to lock
time.sleep(0.015)
# NDAC powered up, NDAC=5
x.tas2505_write(0x0B, 0x85)
# MDAC powered up, MDAC=3
x.tas2505_write(0x0C, 0x83)
# DAC OSR (9:8), DAC OSR = 128
x.tas2505_write(0x0D, 0x00)
# DAC OSR (7:0)
x.tas2505_write(0x0E, 0x80)

# Output DAC_MOD_CLK clock reference using DOUT/GPIO pin
x.tas2505_write(0x19, 0x5)
# Divide DAC_MOD_CLK by 2 to generate a 2.8224MHz reference (44.1kHz, 16bits, stereo) x 2
x.tas2505_write(0x1A, 0x82)
# Set GPIO/DOUT to output CLKOUT
x.tas2505_write(0x34, 0x10)

# Codec interface control, word length = 16b, BCLK & WCLK inputs, LJ mode
x.tas2505_write(0x1B, 0xC0)
# Data slot offset 00
x.tas2505_write(0x1C, 0)
# DAC instruction programming PRB #2 for mono routing. Type interpolation (x8) & 3 programmable biquads
x.tas2505_write(0x3C, 0x2)

x.tas2505_write(0, 1)
# Master reference powered on
x.tas2505_write(0x01, 0x10)
# Output common mode for DAC set to 0.9V (default)
x.tas2505_write(0x0A, 0x00)
# Mixer P output connected to HP out mixer
x.tas2505_write(0x0C, 0x04)
# HP volume, 0dB gain
x.tas2505_write(0x16, 0x50)
# No need to enable mixer M & P, AINL volume, dB gain
x.tas2505_write(0x18, 0x00)
# Power up HP
x.tas2505_write(0x09, 0x20)
# Unmute HP with 6dB gain
x.tas2505_write(0x10, 0x18)
# SPK attn gain set to not blow the speaker up
# 20 keeps the attenution at -10dB, which keeps the power output approximately 1/10th maximum or about 250mW, which is below the maximum rated for the speaker
x.tas2505_write(0x2E, 0)
# SPK driver gain = 6dB
x.tas2505_write(0x30, 0x10)
# SPK powered up
x.tas2505_write(0x2D, 0x02)

x.tas2505_write(0, 0)
# DAC powered up, soft step 1 per Fs
x.tas2505_write(0x3F, 0x90)
# DAC digital gain 0dB
x.tas2505_write(0x41, 0x00)
# DAC volume not muted
x.tas2505_write(0x40, 0x04)

# Wait for the integrator to stabilise
time.sleep(2)
print('Current reference frequency estimate: '+str(x.tas2505_osc_frequency())+'MHz')
time.sleep(0.1)

# Run the microphone test
print('Testing microphone...')
x.mic_demo(args.file, args.length)

