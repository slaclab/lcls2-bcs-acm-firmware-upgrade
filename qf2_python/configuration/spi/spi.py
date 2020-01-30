#!/usr/bin/env python

import time, sys, hashlib

import qf2_python.configuration.spi.constants as spi_constants
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser

# Compatibility layer
if sys.version_info < (3,):
    import qf2_python.compat.python2 as compat
else:
    import qf2_python.compat.python3 as compat

class Generic():
    RDID = 0x9F
    RSTEN = 0x66
    RST = 0x99

    def __init__(self, target):
        self.__target = target

        # Trigger a full reset of the PROM (escapes certain error conditions)
        self.write_register(self.RSTEN)
        time.sleep(0.000001)
        self.write_register(self.RST)
        time.sleep(0.000001)
 
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

# Instructions
class SL25FLL():
    RDID = 0x9F
    RDSR1 = 0x05
    RDSR2 = 0x07
    RDCR1 = 0x35
    RDCR2 = 0x15
    RDCR3 = 0x33

    RDAR = 0x65
    WRAR = 0x71
    WREN = 0x06
    EN4BYTEADDR = 0xB7
    EX4BYTEADDR = 0xE9
    FAST_READ = 0x0B
    FAST_FOUR_BYTE_READ = 0x0C
    ERASE_CHIP = 0x60
    ERASE_4KB = 0x20
    ERASE_64KB = 0xD8
    ERASE_FOUR_BYTE_64KB = 0xDC
    PP = 0x2
    PP_FOUR_BYTE = 0x12

    def __init__(self, target, verbose=False):
        self.__target = target
        self.__verbose = verbose

        # Check if PROM is locked
        self.__locked = (self.read_register(self.RDSR1, 1)[0] >> 7)

        # Read CR3 register and assign current dummy cycle value
        self.__dummy_cycles = self.read_register(self.RDCR3, 1)[0] & 0xF

        # Try to enable 4-byte mode (won't work if PROM is locked and jumper is not on board - undocumented 'feature')
        #self.write_register(self.EN4BYTEADDR)

        # If unlocked, make sure dummy cycles is set to 8 and 4 byte address mode is the default
        if self.__locked == 0:

            # Check CR2NV state
            if (self.read_any_register(bytearray([0x00, 0x00, 0x03]), 1)[0] & 0xFE) != 0x60:

                if verbose==True:
                    print('Setting CR2NV to 0x60')

                # Update CR2NV to 0x11
                self.write_register(self.WREN)
                self.write_register(self.WRAR, bytearray([0x00, 0x00, 0x03, 0x60]))

                while self.read_register(self.RDSR1, 1)[0] & 0x1:
                    continue

                if (self.read_any_register(bytearray([0x00, 0x00, 0x03]), 1)[0] & 0xFE) != 0x60:
                    raise SPI_Base_Exception('Could not set CR2NV to 0x60.')

            # Check CR3NV state
            if (self.read_any_register(bytearray([0x00, 0x00, 0x04]), 1)[0]) != 0x18:

                if verbose==True:
                    print('Setting CR3NV to 0x18')

                # Update CR3NV to 0x11
                self.write_register(self.WREN)
                self.write_register(self.WRAR, bytearray([0x00, 0x00, 0x04, 0x18]))

                while self.read_register(self.RDSR1, 1)[0] & 0x1:
                    continue

                if self.read_any_register(bytearray([0x00, 0x00, 0x04]), 1)[0] != 0x18:
                    raise SPI_Base_Exception('Could not set CR3NV to 0x18.')

        # Read CR3 register and assign dummy cycle value
        self.__dummy_cycles = self.read_register(self.RDCR3, 1)[0] & 0xF

        # Check we are in 4-byte address mode
        #self.__four_byte_mode = True
        #if self.read_register(self.RDCR2, 1)[0] & 2 != 2:
        #    self.__four_byte_mode = False

    def __del__(self):
        # Ensure we return to 3-byte address mode in case someone is doing e.g. multiboot
        # because the Xilinx FPGAs are too stupid to not reinitialise the PROM before use
        #self.write_register(self.EX4BYTEADDR)
        pass

    def lock(self):
        if self.__locked == 1:
            return

        # Make sure CMP is == 0 (i.e. CR1NV is in default state of all zeros)
        self.write_register(self.WREN)
        self.write_register(self.WRAR, bytearray([0x00, 0x00, 0x02, 0x00]))

        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

        if self.read_register(self.RDCR1, 1)[0] != 0:
            raise SPI_Base_Exception('Could not set CR1NV to 0x00. Have you put a jumper on the write protect header?')

        # Set the protection bit
        # TBPROT=1, BP=0110, == 32 lowest sectors (Spartan bootloader + cfg + a few extra sectors for future use)
        self.write_register(self.WREN)
        self.write_register(self.WRAR, bytearray([0x00, 0x00, 0x00, 0xD8]))

        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

        if self.read_register(self.RDSR1, 1)[0] != 0xD8:
            raise SPI_Base_Exception('Could not set SR1NV to 0xD8. Have you put a jumper on the write protect header?')

        self.__locked = 1

    def unlock(self):
        if self.__locked == 0:
            return

        # Release the lock - clear SR1NV
        self.write_register(self.WREN)
        self.write_register(self.WRAR, bytearray([0x00, 0x00, 0x00, 0x00]))

        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            continue

        if self.read_register(self.RDSR1, 1)[0] != 0x00:
            raise SPI_Base_Exception('Could not set SR1NV to 0x00. Have you put a jumper on the write protect header?')

        self.__locked = 0

    def read_any_register(self, address, num_bytes):
        self.__target.write(self.RDAR, 8, False, False, True)
        self.__target.write_bytearray(address, False, True, False)
                                  
        # Dummy cycles (first data on falling edge of last cycle)
        self.__target.jtag_clock(bytearray([0]) * self.__dummy_cycles)
       
        # Read MSB first
        result = self.__target.write_read_bytearray(bytearray([0]) * num_bytes, False, False, True)

        # Last byte raises CS_B
        self.__target.jtag_clock([jtag.TMS])
        return result

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
        #if self.__four_byte_mode == False:
        #    raise SPI_Base_Exception('PROM is in three byte mode - unsupported')

        self.__target.write(self.FAST_FOUR_BYTE_READ, 8, False, False, True)

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
        if self.__locked == 1:
            raise SPI_Base_Exception('Full chip erase not possible - PROM is currently locked')

        # Write enable
        self.write_register(self.WREN)
        self.write_register(self.ERASE_CHIP)

        # Read the status register and wait for completion
        while self.read_register(self.RDSR1, 1)[0] & 0x1:
            print(str(self.read_register(self.RDSR1, 1)[0]))
            continue

    def sector_erase(self, address):
        if (self.__locked == 1) and (address < (32 * 65536)):
            raise SPI_Base_Exception('Data cannot be erased - PROM is currently locked')

        # Write enable
        self.write_register(self.WREN)

        # Erase a sector
        self.__target.write(self.ERASE_FOUR_BYTE_64KB, 8, False, False, True)

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

    def page_program(self, data, address, verify=False):
        if (self.__locked == 1) and (address < (32 * 65536)):
            raise SPI_Base_Exception('Data cannot be erased - PROM is currently locked')

        if len(data) != 256:
            raise SPI_Base_Exception('Data is not size of page')

        # Write enable
        self.write_register(self.WREN)

        # Page program
        self.__target.write(self.PP_FOUR_BYTE, 8, False, False, True)

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

        if ( verify==True ):
            compare_data = self.read_data(address, 256)
            if compare_data != data:
                raise SPI_Base_Exception('Write-verify failed')


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
        self.__dummy_cycles = 8 #10
        
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

    def page_program(self, data, address, verify=False):
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

        if ( verify==True ):
            compare_data = self.read_data(address, 256)
            if compare_data != data:
                raise SPI_Base_Exception('Write-verify failed')

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
                print('Micron manufacturer code found, assuming N25Q')
            self.__interface = N25Q(self.__target, self.__verbose)
        elif self.__manufacturer_id == 0x1:
            if verbose == True:
                print('Cypress manufacturer code found, assuming SL25FL-L')
            self.__interface = SL25FLL(self.__target, self.__verbose)
                
    def dummy_cycles(self):
        return self.__interface.__dummy_cycles

    def prom_size(self):
        return self.__prom_size

    def lock(self):
        return self.__interface.lock()

    def unlock(self):
        return self.__interface.unlock()

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

    def page_program(self, data, address, verify):
        return self.__interface.page_program(data, address, verify)

    def verify_bitfile(self, name, offset):
        
        # Parse the bitfile and extract the bitstream
        data = xilinx_bitfile_parser.bitfile(name).data()

        # Pad the data to the block boundary
        data += bytearray([0xFF]) * (spi_constants.SECTOR_SIZE - len(data) % spi_constants.SECTOR_SIZE)

        last_length = 0
        start_time = time.time()
        num_blocks = len(data) // spi_constants.SECTOR_SIZE

        for i in range(0, num_blocks):

            # Read the sector
            pd = self.read_data((offset + i) * spi_constants.SECTOR_SIZE, spi_constants.SECTOR_SIZE)
            elapsed = time.time() - start_time
            left = elapsed * (num_blocks - i - 1) // (i + 1)
            total = elapsed + left
            output = str(i)+' / '+str(num_blocks-1)+' (Elapsed: '+'{0:.2f}'.format(elapsed)+'s)'
            output = '{:<100}'.format(output)
            x = str('\b' * last_length)
            compat.print_no_return(x+'\b'+output)
            last_length = len(output) + 1

            sector_update = False
            sector_erase = False
            for j in range(0, spi_constants.SECTOR_SIZE):
                if pd[j] != data[i * spi_constants.SECTOR_SIZE + j]:
                    sector_update = True
                    break

            if not(sector_update):
                continue

            print('')
            raise SPI_Base_Exception('Verifying bitfile failed at byte: ' + str(i * spi_constants.SECTOR_SIZE + j))
        
        print('')

    def program_bitfile(self, name, offset):

        # Parse the bitfile and extract the bitstream
        data = xilinx_bitfile_parser.bitfile(name).data()

        # Pad the data to the block boundary
        data += bytearray([0xFF]) * (spi_constants.SECTOR_SIZE - len(data) % spi_constants.SECTOR_SIZE)

        last_length = 0
        start_time = time.time()
        num_blocks = len(data) // spi_constants.SECTOR_SIZE

        for i in range(0, num_blocks):

            # Read the sector
            pd = self.read_data((offset + i) * spi_constants.SECTOR_SIZE, spi_constants.SECTOR_SIZE)
            elapsed = time.time() - start_time
            left = elapsed * (num_blocks - i - 1) // (i + 1)
            total = elapsed + left
            output = str(i)+' / '+str(num_blocks-1)+' (Elapsed: '+'{0:.2f}'.format(elapsed)+'s)'
            output = '{:<50}'.format(output)
            x = str('\b' * last_length)
            compat.print_no_return(x+'\b'+output)
            last_length = len(output) + 1
            sector_update = False
            sector_erase = False
            for j in range(0, spi_constants.SECTOR_SIZE):
                if pd[j] != data[i * spi_constants.SECTOR_SIZE + j]:
                    sector_update = True
                    break

            if not(sector_update):
                continue

            # Only erase the sector if the data that's changed is currently not set to 0xFF
            sector_erase = False
            #sector_erase = True
            for j in range(0, spi_constants.SECTOR_SIZE):
                if pd[j] != data[i * spi_constants.SECTOR_SIZE + j]:
                    if pd[j] != 0xFF:
                        sector_erase = True
                        break

            # Erase if necessary
            if sector_erase:
                self.sector_erase((offset + i) * spi_constants.SECTOR_SIZE)
                compat.print_no_return('ERASED')

            # Program the 256 byte blocks
            for j in range(0, spi_constants.SECTOR_SIZE//256):
                self.page_program(data[j * 256 + i * spi_constants.SECTOR_SIZE : (j+1) * 256 + i * spi_constants.SECTOR_SIZE], j * 256 + ((offset + i) * spi_constants.SECTOR_SIZE), True)

            # Verify
            #pd = self.read_data((offset + i) * constants.SECTOR_SIZE, constants.SECTOR_SIZE)
            #for j in range(0, constants.SECTOR_SIZE):
            #    if pd[j] != data[i * constants.SECTOR_SIZE + j]:
            #        print('')
            #        raise SPI_Base_Exception('Page update' + str(i * constants.SECTOR_SIZE + j) + 'failed')

            print('UPDATED')

        print('')

    def read_hash(self, start_address, num_bytes):
        m = hashlib.sha256()
        m.update(self.read_data(start_address, num_bytes))
        return bytearray(m.digest())
