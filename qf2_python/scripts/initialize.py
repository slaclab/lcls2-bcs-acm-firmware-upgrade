#!/bin/env python

import argparse
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Initialize QF2-pre', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, False)

# Turn on all the board power supplies

x.kintex_vccint_enable()
x.main_3p3v_enable()

x.set_top_fmc_vadj_resistor(0x14)
x.set_bottom_fmc_vadj_resistor(0x0)
x.fmc_vadj_enable()

x.fmc_3p3v_enable()
x.fmc_12v_enable()

x.kintex_1p0v_gtx_enable()
x.kintex_1p2v_gtx_enable()
