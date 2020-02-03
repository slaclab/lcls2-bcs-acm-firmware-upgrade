#!/bin/env python

import argparse, datetime, time

import qf2_python.identifier as identifier
import qf2_python.tests.kintex_interface as kintex_interface

parser = argparse.ArgumentParser(description='Test Kintex monitoring data access', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')

args = parser.parse_args()

# Ensure we are in runtime
identifier.verifyInRuntime(args.target)

# Start the class
x = kintex_interface.interface(args.target)

while True:
    print('')
    print('----------------------------------', datetime.datetime.now(), '----------------------------------')
    # Trigger a monitor readback and print the data
    x.printMonitoringData()
    time.sleep(1)
