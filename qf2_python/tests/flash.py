#!/bin/env python

import argparse

import qf2_python.identifier as identifier
import qf2_python.tests.kintex_interface as kintex_interface

parser = argparse.ArgumentParser(description='Test FLASH PROM page readback', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')
parser.add_argument('-p', '--page', type=int, required=True, help='Page to retrieve')

args = parser.parse_args()

# Ensure we are in runtime
identifier.verifyInRuntime(args.target)

# Start the class
x = kintex_interface.interface(args.target)

# Trigger a monitor readback and print the data
x.printFlashPage(args.page)
