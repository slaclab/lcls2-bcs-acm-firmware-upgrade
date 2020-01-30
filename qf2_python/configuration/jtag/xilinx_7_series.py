#!/usr/bin/env python

import time, sys

# Compatibility layer
if sys.version_info < (3,):
    import qf2_python.compat.python2 as compat
else:
    import qf2_python.compat.python3 as compat

# JTAG codes for 7 series
BYPASS = 0x3F
IDCODE = 0x09
JPROGRAM = 11
CFG_IN = 5
CFG_OUT = 4
JSTART = 12
JSHUTDOWN = 13
ISC_NOOP = 20
USER1 = 2
USER2 = 3
USER3 = 34
USER4 = 35

class interface():
    def __init__(self, target):
        self.target = target

    def program(self, data, position):

        # Start in idle
        self.target.go_to_run_test_idle()

        # IDCODE
        # No safety check on IDCODE match here, should be done beforehand when loading the bitfile
        #self.target.go_to_shift_ir()
        #self.target.write(IDCODE, 6, True)
        #self.target.go_to_run_test_idle()

        #self.target.go_to_shift_dr()
        #if self.target.read(32, True) != self.target.idcode(0):
        #    raise Kintex7_JTAG_Exception('IDCODE doesn\'t match expected target!')
        #self.target.go_to_run_test_idle()

        # BYPASS
        #self.target.go_to_shift_ir()
        #self.target.write(BYPASS, 6, True)
        #self.target.go_to_run_test_idle()

        # Load the JPROGRAM instruction
        self.target.go_to_shift_ir()
        self.target.write(JPROGRAM, 6, True)
        self.target.go_to_run_test_idle()

        # UG470 suggests waiting 10ms, but better approach is to check for INIT_B
        tprev = time.time()
        init = 0

        # to fix timer
        while time.time() - tprev < 2.0:

            # Check for init gone high
            self.target.go_to_shift_ir()
            init = self.target.write_read(ISC_NOOP, 6, True)
            init = init & 0x11
            self.target.go_to_run_test_idle()
            
            if init == 0x11:
                break

        if init != 0x11:
            raise Exception('INIT_B did not go high')

        # Load IR with CFG_IN
        self.target.go_to_shift_ir()
        self.target.write(CFG_IN, 6, True)
        self.target.go_to_run_test_idle()

        # Go to SHIFT_DR
        self.target.go_to_shift_dr()

        # Load the bitstream 
        i = 0
        subarray = data[i : i + 14000]

        # Adapt code to python2 & python3
        compat.print_no_flush('{:<9}'.format(''))        

        while i + 14000 < len(data):
            self.target.write_bytearray(subarray, False, True)
            i = i + 14000
            subarray = data[i : i + 14000]

            # Adapt code to python2 & python3
            compat.print_no_return('\b\b\b\b\b\b\b\b\b\b' + '{:<9}'.format(str((i * 100) // len(data)) + '%'))
            
        print('')

        # Last block
        self.target.write_bytearray(subarray, True, True)
        self.target.go_to_run_test_idle()

        # JSTART
        self.target.go_to_shift_ir()
        self.target.write(JSTART, 6, True)
        self.target.go_to_run_test_idle()

        # Clock 2000 times minimum
        self.target.jtag_clock(bytearray([0]) * 2000)

        # Check for done high
        self.target.go_to_shift_ir()
        status = self.target.write_read(BYPASS, 6, True)
        self.target.go_to_run_test_idle()

        if ((status & 0x31) != 0x31):
            raise Exception('DONE & INIT did not go high after programming')

    def enter_user_1_dr(self):
        self.target.go_to_run_test_idle()
        self.target.go_to_shift_ir()
        self.target.write(USER1, 6, True)
        self.target.go_to_shift_dr()
        self.target.jtag_clock(bytearray([0]))

    def enter_user_2_dr(self):
        self.target.go_to_run_test_idle()
        self.target.go_to_shift_ir()
        self.target.write(USER2, 6, True)
        self.target.go_to_shift_dr()
        self.target.jtag_clock(bytearray([0]))

    def enter_user_3_dr(self):
        self.target.go_to_run_test_idle()
        self.target.go_to_shift_ir()
        self.target.write(USER3, 6, True)
        self.target.go_to_shift_dr()
        self.target.jtag_clock(bytearray([0]))

    def enter_user_4_dr(self):
        self.target.go_to_run_test_idle()
        self.target.go_to_shift_ir()
        self.target.write(USER4, 6, True)
        self.target.go_to_shift_dr()
        self.target.jtag_clock(bytearray([0]))

