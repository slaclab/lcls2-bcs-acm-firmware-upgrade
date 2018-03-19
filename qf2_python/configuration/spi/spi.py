#!/usr/bin/env python

import time, sys, hashlib
from ..jtag import *

# For the Cypress SL25FL-L, these are called 'sector' and 'block' instead
SUBSECTOR_SIZE = 4096
SECTOR_SIZE = 65536

SPI_DOUT = 1
SPI_DIN = 2
SPI_CLK = 4
SPI_CS_B = 8

class Generic():
    RDID = 0x9F

    def __init__(self, target):
        self.__target = target
 
    def read_register(self, instruction, num_bytes):
        self.__target.write(instruction, 8, False, False, True)

        # Read MSB first
        dummy = bytearray([0]) * num_bytes
        result = self.__target.write_read_bytearray(dummy, False, False, True)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        return result

# Instructions
class SL25FLL():
    RDID = 0x9F
    #SR1NV?
    RDSR1 = 0x05
    RDSR2 = 0x07
    RDCR1 = 0x35
    RDCR2 = 0x15
    RDCR3 = 0x33

    WRAR = 0x71
    WREN = 0x06
    #WRENV = 0x50
    EN4BYTEADDR = 0xB7
    EX4BYTEADDR = 0xE9
    FAST_READ = 0x0B
    ERASE_CHIP = 0x60
    ERASE_4KB = 0x20
    ERASE_64KB = 0xD8
    PP = 0x2

    def __init__(self, target, verbose=False):
        self.__target = target
        self.__verbose = verbose
        self.__dummy_cycles = 8
 
        # Set the volatile dummy cycles register and disable wrapping
        self.write_register(self.WREN)
        self.write_register(self.WRAR, bytearray([0x80, 0x00, 0x04, 0x10 | self.__dummy_cycles]))
        #cr3 = self.read_register(self.RDCR3, 1)[0]

        # Set 4 byte addressing mode
        self.write_register(self.EN4BYTEADDR)

    def __del__(self):
        # Ensure we return to 3-byte address mode in case someone is doing e.g. multiboot
        # because the Xilinx FPGAs are too stupid to not reinitialise the PROM before use
        self.write_register(self.EX4BYTEADDR)

    def write_register(self, instruction, value = bytearray([])):
        # MSB first

        self.__target.write(instruction, 8, False, False, True)
        self.__target.write_bytearray(value, False, True, False)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        
    def read_register(self, instruction, num_bytes):
        self.__target.write(instruction, 8, False, False, True)

        # Read MSB first
        dummy = bytearray([0]) * num_bytes
        result = self.__target.write_read_bytearray(dummy, False, False, True)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        return result

    def read_data(self, start_address, num_bytes):
        self.__target.write(self.FAST_READ, 8, False, False, True)

        # 32-bit address
        send = bytearray()
        for i in range(0, 32):
            if (start_address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        # Dummy cycles (first data on falling edge of last cycle)
        for i in range(0, self.__dummy_cycles):
            send += bytearray([0])

        self.__target.jtag_clock(send)

        send = bytearray([0]) * num_bytes
        result = self.__target.write_read_bytearray(send, False, False, True)

        self.__target.jtag_clock([jtag.TMS])

        return result

    def chip_erase(self, address):

        # Write enable
        self.write_register(self.WREN)
        self.write_register(self.ERASE_CHIP)

        # Read the status register and wait for completion
        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

    def sector_erase(self, address):

        # Write enable
        self.write_register(self.WREN)

        # Erase a sector
        self.__target.write(self.ERASE_64KB, 8, False, False, True)

        # 32-bit address
        send = bytearray()
        for i in range(0, 32):
            if (address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        self.__target.jtag_clock(send)
        self.__target.jtag_clock([jtag.TMS])

        # Read the status register and wait for completion
        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

    def page_program(self, data, address):
        if len(data) != 256:
            raise SPI_Base_Exception('Data is not size of page')

        # Write enable
        self.write_register(self.WREN)

        # Page program
        self.__target.write(self.PP, 8, False, False, True)

        send = bytearray()
        for i in range(0, 32):
            if (address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        self.__target.jtag_clock(send)
        self.__target.write_bytearray(data, False, True, False)

        # Complete transaction
        self.__target.jtag_clock([jtag.TMS])

        # Read the status register and wait for completion
        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

class N25Q():
    RDID = 0x9F
    EN4BYTEADDR = 0xB7
    EX4BYTEADDR = 0xE9
    RDVCR = 0x85
    WRVCR = 0x81
    RDVECR = 0x65
    WRVECR = 0x61
    FAST_READ = 0x0B
    WREN = 0x6
    RDSR = 0x5
    SSE = 0x20
    SE = 0xD8
    PP = 0x2
    RFSR = 0x70
    RESET_ENABLE = 0x66
    RESET_MEMORY = 0x99

    def __init__(self, target, verbose=False):
        self.__target = target
        self.__verbose = verbose
        self.__dummy_cycles = 10
        
        # Set the dummy cycles in the PROM configuration register
        vcr = self.read_register(self.RDVCR, 1)[0]
        vcr &= 0xF & vcr
        vcr |= self.__dummy_cycles << 4
        self.write_register(self.WREN)
        self.write_register(self.WRVCR, bytearray([vcr]))
            
        # Set 4 byte addressing mode
        self.write_register(self.WREN)
        self.write_register(self.EN4BYTEADDR)
        
    def __del__(self):
        # Ensure we return to 3-byte address mode in case someone is doing e.g. multiboot
        # because the Xilinx FPGAs are too stupid to not reinitialise the PROM before use
        self.write_register(self.WREN)
        self.write_register(self.EX4BYTEADDR)
        #print 'Exited 4 byte address mode during cleanup'
        
    def write_register(self, instruction, value = bytearray([])):
        # MSB first
        self.__target.write(instruction, 8, False, False, True)
        self.__target.write_bytearray(value, False, True, False)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        
    def read_register(self, instruction, num_bytes):
        self.__target.write(instruction, 8, False, False, True)

        # Read MSB first
        dummy = bytearray([0]) * num_bytes
        result = self.__target.write_read_bytearray(dummy, False, False, True)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        return result

    def read_data(self, start_address, num_bytes):
        self.__target.write(self.FAST_READ, 8, False, False, True)

        # 32-bit address
        send = bytearray()
        for i in range(0, 32):
            if (start_address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        # Dummy cycles (first data on falling edge of last cycle)
        for i in range(0, self.__dummy_cycles):
            send += bytearray([0])

        self.__target.jtag_clock(send)

        send = bytearray([0]) * num_bytes
        result = self.__target.write_read_bytearray(send, False, False, True)

        self.__target.jtag_clock([jtag.TMS])

        return result

    def sector_erase(self, address):

        # Write enable
        self.write_register(self.WREN)

        # Erase a sector
        self.__target.write(self.SE, 8, False, False, True)

        # 32-bit address
        send = bytearray()
        for i in range(0, 32):
            if (address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        self.__target.jtag_clock(send)
        self.__target.jtag_clock([jtag.TMS])

        # Read the status register and wait for completion
        x = self.read_register(self.RDSR, 1)[0]
        y = self.read_register(self.RFSR, 1)[0]
        while True:
            #print hex(x), hex(y),
            if ((x & 0x1) == 0) and ((y & 0x81) == 0x81):
                break
            x = self.read_register(self.RDSR, 1)[0]
            y = self.read_register(self.RFSR, 1)[0]

    def subsector_erase(self, address):

        # Write enable
        self.write_register(self.WREN)

        # Erase a sector
        self.__target.write(self.SSE, 8, False, False, True)

        # 32-bit address
        send = bytearray()
        for i in range(0, 32):
            if (address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        self.__target.jtag_clock(send)
        self.__target.jtag_clock([jtag.TMS])

        # Read the status register and wait for completion
        x = self.read_register(self.RDSR, 1)[0]
        y = self.read_register(self.RFSR, 1)[0]
        while True:
            #print hex(x), hex(y),
            if ((x & 0x1) == 0) and ((y & 0x81) == 0x81):
                break
            x = self.read_register(self.RDSR, 1)[0]
            y = self.read_register(self.RFSR, 1)[0]

    def page_program(self, data, address):
        if len(data) != 256:
            raise SPI_Base_Exception('Data is not size of page')

        # Write enable
        self.write_register(self.WREN)

        # Page program
        self.__target.write(self.PP, 8, False, False, True)

        send = bytearray()
        for i in range(0, 32):
            if (address >> 31 - i) & 0x1:
                send += bytearray([jtag.TDI])
            else:
                send += bytearray([0])

        self.__target.jtag_clock(send)
        self.__target.write_bytearray(data, False, True, False)

        # Complete transaction
        self.__target.jtag_clock([jtag.TMS])

        # Read the status register and wait for completion
        while self.read_register(self.RDSR, 1)[0] & 0x1:
            continue

class SPI_Base_Exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class interface():
    def __init__(self, chain, verbose=False):
        self.__verbose = verbose
        self.__target = chain

        # Flush the CS_B pin
        self.__target.jtag_clock([jtag.TMS])
        self.__target.state = jtag.states.SHIFT_DR

        self.__interface = Generic(self.__target)

        # Read the device ID information
        x = self.read_register(Generic.RDID, 3)

        if x[2] != 0x19:
            raise SPI_Base_Exception('Size of PROM is not 256Mb ('+str(x[2])+')')
        
        self.__manufacturer_id = x[0]
        self.__prom_size = x[2]

        if self.__manufacturer_id == 0x20:
            if verbose == True:
                print 'Micron manufacturer code found, assuming N25Q'
            self.__interface = N25Q(self.__target, self.__verbose)
        elif self.__manufacturer_id == 0x1:
            if verbose == True:
                print 'Cypress manufacturer code found, assuming SL25FL-L'
            self.__interface = SL25FLL(self.__target, self.__verbose)
                
    def dummy_cycles(self):
        return self.__interface.__dummy_cycles

    def prom_size(self):
        return self.__prom_size

    def write_register(self, instruction, value = bytearray([])):
        return self.__interface.write_register(instruction, value)
        
    def read_register(self, instruction, num_bytes):
        return self.__interface.read_register(instruction, num_bytes)

    def read_data(self, start_address, num_bytes):
        return self.__interface.read_data(start_address, num_bytes)

    def sector_erase(self, address):
        return self.__interface.sector_erase(address)

    def subsector_erase(self, address):
        return self.__interface.subsector_erase(address)

    def page_program(self, data, address):
        return self.__interface.page_program(data, address)

    def verify_bitfile(self, name, offset):
        print offset
        
        # Parse the bitfile and extract the bitstream
        data = xilinx_bitfile_parser.bitfile(name).data()

        # Pad the data to the block boundary
        data += bytearray([0xFF]) * (SECTOR_SIZE - len(data) % SECTOR_SIZE)

        last_length = 0
        start_time = time.time()
        num_blocks = len(data) / SECTOR_SIZE

        for i in range(0, num_blocks):

            # Read the sector
            pd = self.read_data((offset + i) * SECTOR_SIZE, SECTOR_SIZE)
            elapsed = time.time() - start_time
            left = elapsed * (num_blocks - i - 1) / (i + 1)
            total = elapsed + left
            output = str(i)+' / '+str(num_blocks-1)+' (Elapsed: '+str(elapsed)+'s, Left: '+str(left)+'s, Total: '+str(total)+'s)'
            output = '{:<100}'.format(output)
            x = str('\b' * last_length)
            print x, '\b'+output,
            sys.stdout.flush()
            last_length = len(output) + 1

            sector_update = False
            sector_erase = False
            for j in range(0, SECTOR_SIZE):
#                print hex(pd[j]), ',', hex(data[i * SECTOR_SIZE + j])
                if pd[j] != data[i * SECTOR_SIZE + j]:
                    sector_update = True
                    break

            if not(sector_update):
                continue

            raise SPI_Base_Exception('Verifying bitfile failed at byte: ' + str(i * SECTOR_SIZE + j))

        print

    def program_bitfile(self, name, offset):

        # Parse the bitfile and extract the bitstream
        data = xilinx_bitfile_parser.bitfile(name).data()

        # Pad the data to the block boundary
        data += bytearray([0xFF]) * (SECTOR_SIZE - len(data) % SECTOR_SIZE)

        last_length = 0
        start_time = time.time()
        num_blocks = len(data) / SECTOR_SIZE

        for i in range(0, num_blocks):

            # Read the sector
            pd = self.read_data((offset + i) * SECTOR_SIZE, SECTOR_SIZE)
            elapsed = time.time() - start_time
            left = elapsed * (num_blocks - i - 1) / (i + 1)
            total = elapsed + left
            output = str(i)+' / '+str(num_blocks-1)+' (Elapsed: '+str(elapsed)+'s, Left: '+str(left)+'s, Total: '+str(total)+'s)'
            output = '{:<100}'.format(output)
            x = str('\b' * last_length)
            print x, '\b'+output,
            #print output,
            sys.stdout.flush()
            last_length = len(output) + 1

            sector_update = False
            sector_erase = False
            for j in range(0, SECTOR_SIZE):
                if pd[j] != data[i * SECTOR_SIZE + j]:
                    sector_update = True
                    break

            if not(sector_update):
                continue

            # Only erase the sector if the data that's changed is currently not set to 0xFF
            sector_erase = False
            #sector_erase = True
            for j in range(0, SECTOR_SIZE):
                if pd[j] != data[i * SECTOR_SIZE + j]:
                    if pd[j] != 0xFF:
                        sector_erase = True
                        break

            # Erase if necessary
            if sector_erase:
                self.sector_erase((offset + i) * SECTOR_SIZE)
                print 'ERASED',

            # Program the 256 byte blocks
            for j in range(0, SECTOR_SIZE/256):
                self.page_program(data[j * 256 + i * SECTOR_SIZE : (j+1) * 256 + i * SECTOR_SIZE], j * 256 + ((offset + i) * SECTOR_SIZE))

            # Verify
            pd = self.read_data((offset + i) * SECTOR_SIZE, SECTOR_SIZE)
            for j in range(0, SECTOR_SIZE):
                if pd[j] != data[i * SECTOR_SIZE + j]:
                    print
                    raise SPI_Base_Exception('Page update' + str(i * SECTOR_SIZE + j) + 'failed')

            print 'UPDATED'

        print

    def read_hash(self, start_address, num_bytes):
        m = hashlib.sha256()
        m.update(self.read_data(start_address, num_bytes))
        return bytearray(m.digest())
