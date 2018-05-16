#!/bin/env python

from socket import *
import string, time, sys
from datetime import datetime, timedelta

class QSFP_INFO:
        IDENTIFIER = {
                1 : 'GBIC',
                2 : 'Module / connector soldered to motherboard',
                3 : 'SFP or SFP+',
                4 : '300 pin XBI',
                5 : 'XENPAK',
                6 : 'XFP',
                7 : 'XFF',
                8 : 'XFP-E',
                9 : 'XPAK',
                10 : 'X2',
                11 : 'DWDM-SFP',
                12 : 'QSFP',
                13 : 'QSFP+',
                14 : 'CXP'
                }

        STATUS = {
                0 : 'PAGED UPPER MEMORY, INTERRUPT ACTIVE, MEMORY DATA READY',
                1 : 'PAGED UPPER MEMORY, INTERRUPT ACTIVE, MEMORY DATA NOT READY',
                2 : 'PAGED UPPER MEMORY, INTERRUPT INACTIVE, MEMORY DATA READY',
                3 : 'PAGED UPPER MEMORY, INTERRUPT INACTIVE, MEMORY DATA NOT READY',
                4 : 'NO UPPER MEMORY, INTERRUPT ACTIVE, MEMORY DATA READY',
                5 : 'NO UPPER MEMORY, INTERRUPT ACTIVE, MEMORY DATA NOT READY',
                6 : 'NO UPPER MEMORY, INTERRUPT INACTIVE, MEMORY DATA READY',
                7 : 'NO UPPER MEMORY, INTERRUPT INACTIVE, MEMORY DATA NOT READY',
                }

class SI570:
        HSDIV_2_0_N1_6_2 = 7
        N1_1_0_RFREQ_37_32 = 8
        RFREQ_31_24 = 9
        RFREQ_23_16 = 10
        RFREQ_15_8 = 11
        RFREQ_7_0 = 12
        SETTINGS = 135
        FREEZE_DCO = 137

class PCA9534:
	INPUT = 0
	OUTPUT = 1
	POLARITY = 2
	DIRECTION = 3

class LTC2990:
	STATUS = 0
	CONTROL = 1
	TRIGGER = 2
	T_MSB = 4
	T_LSB = 5
	V1_MSB = 6
	V1_LSB = 7
	V2_MSB = 8
	V2_LSB = 9
	V3_MSB = 10
	V3_LSB = 11
	V4_MSB = 12
	V4_LSB = 13
	VCC_MSB = 14
	VCC_LSB = 15

def conv_n(x, n):
	if x > (2**(n-1) - 1):
		x = x - 2**n
	return x

class cfg:

        class SHA256(object):

                def __init__(self, val):
                        if type(val) == str:
                                if (len(val) != 64):
                                        raise Exception('Bad SHA256 hash argument')
                                self.__val = list([0] * 32)
                                for i in range(0, 32):
                                        self.__val[i] = int(val[i*2:i*2+2], 16)
                                return
                        if type(val) == bytearray:
                                if (len(val) != 32):
                                        raise Exception('Bad SHA256 hash argument')
                                self.__val = list([0] * 32)
                                for i in range(0, 32):
                                        self.__val[i] = int(val[i])
                                return                                
                        raise Exception('Invalid type assignment')

                def __int__(self):
                        x = 0
                        for i in range(0, 32):
                                x = x | (int(self.__val[i]) << 8 * i)
                        return x

                def __get__(self, objtype=None):
                        return self.__val

                def __set__(self, val):
                        return
        
                # Pretty output
                def __str__(self):
                        s = str()
                        for i in range(0, 32):
                                s += '{:02x}'.format(self.__val[i])
                        return s[:-1]

        class IPV4_IP(object):

                def __init__(self, val):
                        if type(val) == str:
                                ip = val.split('.')
                                if (len(ip) != 4):
                                        raise Exception('Bad IPv4 address argument')
                                x = 0
                                for i in range(0, 4):
                                        x = x | (int(ip[i]) << ((3-i)*8))
                                val = x
                        if type(val) == bytearray:
                                if len(val) != 4:
                                        raise Exception('Value is too large')
                                x = 0
                                for i in range(0, 4):
                                        x = x | (int(val[i]) << (i*8))
                                val = x
                        if val > (2**32)-1:
                                raise Exception('Value is too large')
                        self.__val = val

                def __int__(self):
                        return self.__val

                def __get__(self, objtype=None):
                        return self.__val

                def __set__(self, val):
                        return
        
                # Pretty output
                def __str__(self):
                        s = str()
                        for i in range(0, 4):
                                s += '{:d}'.format((self.__val >> ((3-i) * 8)) & 0xFF) + '.'
                        return s[:-1]

        class IPV4_PORT(object):

                def __init__(self, val):
                        if type(val) == str:
                                val = int(val)
                        if type(val) == bytearray:
                                if len(val) != 2:
                                        raise Exception('Value is too large')
                                x = 0
                                for i in range(0, 2):
                                        x = x | (int(val[i]) << (i*8))
                                val = x
                        if val > 2**16-1:
                                raise Exception('Value is too large')
                        self.__val = val

                def __int__(self):
                        return self.__val

                def __get__(self, objtype=None):
                        return self.__val

                def __set__(self, val):
                        return
        
                # Pretty output
                def __str__(self):
                        return str(self.__val)

        class IPV4_MAC(object):

                def __init__(self, val):
                        if type(val) == str:
                                mac = val.split(':')
                                if (len(mac) != 6):
                                        raise Exception('Bad MAC address argument')
                                x = 0
                                for i in range(0, 6):
                                        x = x | (int(mac[i], 16) << ((5-i)*8))
                                val = x
                        if type(val) == bytearray:
                                if len(val) != 6:
                                        raise Exception('Value is too large')
                                x = 0
                                for i in range(0, 6):
                                        x = x | (int(val[i]) << (i*8))
                                val = x
                        if val > 2**48-1:
                                raise Exception('Value is too large')
                        self.__val = val

                def __int__(self):
                        return self.__val

                def __get__(self, objtype=None):
                        return self.__val

                def __set__(self, val):
                        return
        
                # Pretty output
                def __str__(self):
                        s = str()
                        for i in range(0, 6):
                                s += '{:02X}'.format((self.__val >> ((5-i) * 8)) & 0xFF) + ':'
                        return s[:-1]

        def __init__(self, verbose):
                self.__verbose = verbose
                self.__WRITE_LENGTH = 63
                self.__READ_LENGTH = 59
                self.__NETWORK_LENGTH = 22

                # Key : [Start (bits), Length (bits), Type / Default]
                self.__network_cfg = {

                        'IPV4_MULTICAST_MAC' : [128, 48, self.IPV4_MAC(0)],
                        'IPV4_MULTICAST_IP' : [96, 32, self.IPV4_IP(0)],
                        'IPV4_MULTICAST_PORT' : [80, 16, self.IPV4_PORT(0)],

                        'IPV4_UNICAST_MAC' : [32, 48, self.IPV4_MAC(0xAABBCCDDEEFF)],
                        'IPV4_UNICAST_IP' : [0, 32, self.IPV4_IP(0xC0A8017F)]

                        }

                # Key : [Start (bits), Length (bits), Type / Default]
                self.__write_cfg = {

                        # SYS I2C DEBUG IGNORED

                        '__N_TAS_2505_RESET' : [10, 1, int(0)],

                        'AUTOBOOT_TO_RUNTIME' : [4, 1, int(0)],

                        'SYS_I2C_RESET' : [2, 1, int(1)],
                        'SYS_I2C_SDA' : [1, 1, int(1)],
                        'SYS_I2C_SCL' : [0, 1, int(1)]

                        }
                                        
                # Key : [Start (bits), Length (bits), Type]
                self.__read_cfg = {

                        #TAS COUNT, CORRUPTED BITSTREAM, FLASH DEBUG

                        'ATSHA204_ERROR' : [51*8+4, 1, int()],
                        'ATSHA204_DONE' : [51*8+3, 1, int()],
                        '__FAN_TACH' : [51*8+2, 1, int()],
                        '__N_IS_QF2P' : [51*8+1, 1, int()],
                        '__JACK_SENSE' : [51*8, 1, int()],

                        '__BOARD_UID' : [4*8, 72, int()],
                        '__MDIO_EXTENDED_STATUS' : [2*8, 16, int()],
                        '__MDIO_BASIC_STATUS' : [0, 16, int()],

                        }

                if self.__verbose == True:
                        print('')
                        print('Initial default network configuration is:')
                        print('')
                        self.print_network_cfg()
                        print('')
                        print('Initial default write configuration is:')
                        print('')
                        self.print_write_cfg()
                        print('')
                        print('Initial default read configuration is:')
                        print('')
                        self.print_read_cfg()
                        print('')

                # Check if we are running standalone or inherited
                if 'get_bytes' in dir(self):
                        if self.__verbose == True:
                                print('Querying board status...')
                                print('')

                        self.import_network_data()

                        if self.__verbose == True:
                                print('Current network configuration is:')
                                print('')
                                self.print_network_cfg()
                                print('')
                                print('Current write configuration is:')
                                print('')
                                self.print_write_cfg()
                                print('')
                                print('Current read configuration is:')
                                print('')
                                self.print_read_cfg()
                                print('')

        def import_network_data(self):

                x = self.get_bytes()
                
                read_block = x[0:self.__READ_LENGTH]
                write_block = x[self.__READ_LENGTH:self.__WRITE_LENGTH+self.__READ_LENGTH]
                network_block = x[self.__READ_LENGTH+self.__WRITE_LENGTH:]

                for key, value in self.__network_cfg.items():
                        self.__import_cfg_value(key, self.__network_cfg, network_block)

                for key, value in self.__read_cfg.items():
                        self.__import_cfg_value(key, self.__read_cfg, read_block)

                for key, value in self.__write_cfg.items():
                        self.__import_cfg_value(key, self.__write_cfg, write_block)

        def is_network_key(self, key):
                return key in self.__network_cfg

        def is_write_key(self, key):
                return key in self.__write_cfg

        def set_write_key(self, key, value):
                # Just pass the underlying integer if the default is integer
                if (type(self.__write_cfg[key][2]) == int) or (type(self.__write_cfg[key][2]) == long):
                        self.__write_cfg[key][2] = int(value, 0)
                        return

                self.__write_cfg[key][2] = type(self.__write_cfg[key][2])(value)

        def set_network_key(self, key, value):
                # Just pass the underlying integer if the default is integer
                if (type(self.__network_cfg[key][2]) == int) or (type(self.__network_cfg[key][2]) == long):
                        self.__network_cfg[key][2] = int(value, 0)
                        return

                self.__network_cfg[key][2] = type(self.__network_cfg[key][2])(value)

        def print_network_cfg(self):
                for key, value in sorted(self.__network_cfg.items()):
                        print(key+' : '+str(value[2]))

        def print_write_cfg(self):
                for key, value in sorted(self.__write_cfg.items()):
                        print(key+' : '+str(value[2]))

        def print_read_cfg(self):
                for key, value in sorted(self.__read_cfg.items()):
                        print(key+' : '+str(value[2]))

        def __export_cfg_value(self, value):
                return int(value[2]) << value[0]

        def export_prom_data(self):

                result = bytearray(self.__WRITE_LENGTH + self.__NETWORK_LENGTH)

                total = 0
                for key, value in self.__write_cfg.items():
                        x = self.__export_cfg_value(value)
                        total = total | x

                for i in range(0, self.__WRITE_LENGTH):
                        result[i] = total & 0xFF
                        total = total >> 8

                total = 0
                for key, value in self.__network_cfg.items():
                        x = self.__export_cfg_value(value)
                        total = total | x

                for i in range(0, self.__NETWORK_LENGTH):
                        result[i + self.__WRITE_LENGTH] = total & 0xFF
                        total = total >> 8

                result.reverse()

                v = self.fletcher_check(result)
                result += v
                result += bytearray([0xFF]) * (256 - len(result))

                return result

        def __import_cfg_value(self, key, target, data):
                value = target[key]
                start_point = int(value[0])
                bit_length = int(value[1])
                block = bytearray()

                print key
                print start_point
                print bit_length
                
                # Parse into an integer, then shift and mask
                myi = 0
                start = (start_point >> 3)
                end = start + (bit_length >> 3) + 2
                if end > len(data):
                        end = len(data)
                for i in range(start, end):
                        myi = myi | (int(data[i]) << ((i-start)*8))

                # Generate the mask
                mask = 0
                for i in range(0, bit_length):
                        mask = (mask << 1) | 1
                
                # Shift the data down to align and mask off
                myi = (myi >> (start_point & 0x7)) & mask

                # Convert the integer into a bytearray
                num_bytes = (bit_length / 8)
                if (bit_length & 0x7) != 0:
                        num_bytes += 1

                # Just pass the underlying integer if the default is integer
                if (type(target[key][2]) == int) or (type(target[key][2]) == long):
                        target[key][2] = myi
                        return

                # Otherwise pass a block
                for i in range(0, num_bytes):
                        block.append(myi & 0xFF)
                        myi = myi >> 8

                target[key][2] = type(target[key][2])(block)

        def import_prom_data(self, data):

                v = self.fletcher_check(data[0:self.__WRITE_LENGTH + self.__NETWORK_LENGTH])

                if ( v != data[self.__WRITE_LENGTH + self.__NETWORK_LENGTH:self.__WRITE_LENGTH + self.__NETWORK_LENGTH+2] ):
                        # Invalid checksum
                        print('Imported PROM data checksum is invalid, configuration will not be imported')
                        return False

                # Reverse so ordering matches VHDL
                rdata = data[0:self.__WRITE_LENGTH+self.__NETWORK_LENGTH]
                rdata.reverse()

                for key, value in self.__write_cfg.items():
                        self.__import_cfg_value(key, self.__write_cfg, rdata[0:self.__WRITE_LENGTH])

                # Import each value one by one from the PROM data
                for key, value in self.__network_cfg.items():
                        self.__import_cfg_value(key, self.__network_cfg, rdata[self.__WRITE_LENGTH:self.__NETWORK_LENGTH+self.__WRITE_LENGTH])

                return True

        def network_length(self):
                return self.__NETWORK_LENGTH
        def write_length(self):
                return self.__WRITE_LENGTH
        def read_length(self):
                return self.__READ_LENGTH
        def packet_receive_length(self):
                return self.__READ_LENGTH + self.__WRITE_LENGTH + self.__NETWORK_LENGTH

        def fletcher(self, data):

                sum1 = 0xAA
                sum2 = 0x55
                for i in data:
                        sum1 = sum1 + int(i)
                        sum2 = sum1 + sum2

                sum1 = sum1 % 255
                sum2 = sum2 % 255

                return bytearray([sum1, sum2])

        def fletcher_check(self, data):
                
                v = self.fletcher(data)

                sum1 = 0xFF - ((int(v[0]) + int(v[1])) % 255)
                sum2 = 0xFF - ((int(v[0]) + sum1) % 255)

                return bytearray([sum1, sum2])

class interface(cfg):

        def __init__(self, host, verbose):

                # Settings
                self.__host = host
                self.__port = 50001
                self.__i2c_port = 50002
                self.BOARD_UID = str()

                # Interface socket
                self.UDPSock = socket(AF_INET,SOCK_DGRAM)
                self.UDPSock.bind(("0.0.0.0", 0))
                self.UDPSock.settimeout(2)

                # External I2C socket
                self.I2CSock = socket(AF_INET, SOCK_DGRAM)
                self.I2CSock.bind(("0.0.0.0", 0))
                self.I2CSock.settimeout(2)

                # Initialize the configuration layer
                cfg.__init__(self, verbose)

                while True:

                        try:
                                # Pull the board ID
                                cfg0 = self.atsha204_cfg_read(0)
                                cfg2 = self.atsha204_cfg_read(2)
                                cfg3 = self.atsha204_cfg_read(3)

                                serial_number = 0
                                serial_number |= (cfg3[0] << (8 * 8))
                                serial_number |= (cfg2[3] << (8 * 7))
                                serial_number |= (cfg2[2] << (8 * 6))
                                serial_number |= (cfg2[1] << (8 * 5))
                                serial_number |= (cfg2[0] << (8 * 4))
                                serial_number |= (cfg0[3] << (8 * 3))
                                serial_number |= (cfg0[2] << (8 * 2))
                                serial_number |= (cfg0[1] << (8 * 1))
                                serial_number |= cfg0[0]

                                self.BOARD_UID = '{:018X}'.format(serial_number)
                                print
                                print('Board UID: '+self.BOARD_UID)

                        except:
                                raise

                raise Exception('This is an intentional exception - the bootloader interface is a placeholder for future use.')

        def atsha204_wake(self):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                addr_r = int('{:08b}'.format(0xC9)[::-1], 2)
                
                self.i2c_start()
                time.sleep(0.00006) # SDA low for at least 60us
                self.i2c_stop()
                time.sleep(0.0025) # Wait at least 2.5ms

                # Should be awake now

                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                l =  self.i2c_read()
                self.i2c_clk(0)

                if l != 4:
                        self.i2c_stop()
                        raise Exception('Failed to wake ATSHA204A')

                l = self.i2c_read()
                self.i2c_clk(0)

                if l != 0x11:
                        self.i2c_stop()
                        raise Exception('Failed to wake ATSHA204A')

                l = self.i2c_read()
                self.i2c_clk(0)

                if l != 0x33:
                        self.i2c_stop()
                        raise Exception('Failed to wake ATSHA204A')

                l = self.i2c_read()
                self.i2c_clk(1)
                self.i2c_stop()

                if l != 0x43:
                        raise Exception('Failed to wake ATSHA204A')

        def atsha204_sleep(self):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                word = int('{:08b}'.format(0x01)[::-1], 2)

                self.i2c_start()
                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(word)
                self.i2c_check_ack()
                self.i2c_stop()

        def atsha204_idle(self):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                word = int('{:08b}'.format(0x02)[::-1], 2)

                self.i2c_start()
                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(word)
                self.i2c_check_ack()
                self.i2c_stop()

        def crc16_arc(self, data):
                generator = 0x8005
                crc = 0

                for d in data:

                        crc = crc ^ (int('{:08b}'.format(d)[::-1], 2) << 8)

                        for i in range(0, 8):
                                crc = crc << 1
                                if ( (crc & 0x10000) != 0 ):
                                        crc = (crc & 0xFFFF) ^ generator
                
                return crc

        # read 0x02
        def atsha204_cfg_read(self, radd):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                addr_r = int('{:08b}'.format(0xC9)[::-1], 2)
                word = int('{:08b}'.format(0x03)[::-1], 2)
                count = int('{:08b}'.format(0x07)[::-1], 2)
                cmd = int('{:08b}'.format(0x02)[::-1], 2)

                crc = self.crc16_arc([0x07, 0x02, 0x00, radd, 0x00])                
                crcl = int('{:08b}'.format(crc & 0xFF)[::-1], 2)
                crch = int('{:08b}'.format(crc >> 8)[::-1], 2)

                print hex(crc & 0xFF), hex(crc >>8)

                radd = int('{:08b}'.format(radd)[::-1], 2)

                # Set the chain
                self.i2c_chain_set(0x8)

                # Wake the device
                self.atsha204_wake()

                self.i2c_start()
                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(word)
                self.i2c_check_ack()
                self.i2c_write(count) # count + crc(2) + opcode + param1 + param2(2)
                self.i2c_check_ack()
                self.i2c_write(cmd) # 0x02
                self.i2c_check_ack()
                self.i2c_write(0) # param1
                self.i2c_check_ack()
                self.i2c_write(radd) # param2 (addr)
                self.i2c_check_ack()
                self.i2c_write(0) # param2
                self.i2c_check_ack()
                self.i2c_write(crcl) # crc lsb
                self.i2c_check_ack()
                self.i2c_write(crch) # crc msb
                self.i2c_check_ack()
                self.i2c_stop()

                # wait texec (max) for read
                time.sleep(0.004)

                # Read (must be done by now)
                v = list()
                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                v.append(self.i2c_read())
                self.i2c_clk(0)

                for i in range(1, v[0]-1):
                        v.append(self.i2c_read())
                        self.i2c_clk(0)

                v.append(self.i2c_read())
                self.i2c_clk(1) # NACK
                self.i2c_stop()

                if (self.crc16_arc(v[0:-2]) != ((v[-1] << 8) | v[-2])):
                        raise Exception('CRC error reading ATSHA204A')

                print len(v)

                # Sleep the device
                self.atsha204_sleep()

                return v[1:5]


        def i2c_chain_set(self, value):
                # Reset the mux first
                self.set_byte(0, 0x3, 0x7)
                self.set_byte(0, 0x7, 0x7)

                address = 0xE0
                address = int('{:08b}'.format(address)[::-1], 2)
                value = int('{:08b}'.format(value)[::-1], 2)

                self.i2c_start()

                self.i2c_write(address)
                self.i2c_check_ack()
                self.i2c_write(value)
                self.i2c_check_ack()

                self.i2c_stop()
               
        def i2c_chain_get(self):
                address = 0xE1
                address = int('{:08b}'.format(address)[::-1], 2)

                self.i2c_start()

                self.i2c_write(address)
                self.i2c_check_ack()
                
                result = self.i2c_read()
                self.i2c_clk(1)
                
                self.i2c_stop()
                
                return result


        def i2c_clk(self, bit):
                
                # Isolate reset bits with clock low and set data bit
                self.set_byte(0, ((bit & 1) << 1), 0x3)
                
                # Set clock high
                self.set_byte(0, 0x1, 0x1)

                # Sample bit
                result = int(self.get_byte(48) & 0x2) >> 1
               
                # Bring clock low
                self.set_byte(0, 0, 0x1)

                # Bring data low
                self.set_byte(0, 0, 0x2)
                
                return result

        def i2c_start(self):

                # Bring clock and data high
                self.set_byte(0, 0x3, 0x3)

                # Bring data low
                self.set_byte(0, 0, 0x2)

                # Bring clock low
                self.set_byte(0, 0, 0x1)

        def i2c_repeated_start(self):

                # Bring data high
                self.set_byte(0, 0x2, 0x2)

                # Bring clock high
                self.set_byte(0, 0x1, 0x1)

                # Bring data low
                self.set_byte(0, 0, 0x2)

                # Bring clock low
                self.set_byte(0, 0, 0x1)

        def i2c_stop(self):

                # Bring clock high
                self.set_byte(0, 0x1, 0x1)

                # Bring data high
                self.set_byte(0, 0x2, 0x2)
              
        def i2c_write(self, value):
                
                for i in range(0, 8):
                        self.i2c_clk(value & 0x1)
                        value = value >> 1

        def i2c_read(self):
                       
                result = int()
                for i in range(0, 8):
                        bit = self.i2c_clk(1)
                        result = (result << 1) | bit

                return result

        def i2c_check_ack(self, must_ack = True):
                
                if self.i2c_clk(1) == 1:
                        if ( must_ack ):
                                raise Exception('I2C acknowledge failed')
                        else:
                                return False

                return True



























        def set_byte(self, index, data, mask):
                d = bytearray(cfg.write_length(self))
                m = bytearray(cfg.write_length(self))
                d[index] = data
                m[index] = mask
                self.send_receive(d, m)

        def get_byte(self, index):
                d = bytearray(cfg.write_length(self))
                m = bytearray(cfg.write_length(self))
                res = self.send_receive(d, m)
                return res[index]

        def get_bytes(self):
                d = bytearray(cfg.write_length(self))
                m = bytearray(cfg.write_length(self))
                return self.send_receive(d, m)

        def send_receive(self, data, mask):
                data.reverse()
                mask.reverse()
                rbytes = bytearray()
                rbytes[:] = (mask + data)
                
                read_bytes = str()

                while True:
                        try:
                                self.UDPSock.sendto(str(rbytes),(self.__host, self.__port))
                                read_bytes = self.UDPSock.recv(cfg.packet_receive_length(self))
                                if not read_bytes:
                                        print('No data received')
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

                res = bytearray(read_bytes)
                res.reverse()
                return res

        def reboot_to_runtime(self, wait_for_reboot=False):
                x = bytearray([0x81])
                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.sendto(x,(self.__host,50000))
                TempSock.close()

                if wait_for_reboot == False:
                        return

                # Wait two seconds for board to enter reset phase
                time.sleep(2)
                
                # Loop wait for reboot
                print('Waiting for board to reconnect...')
                x = bytearray([0x0])
                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.bind(("0.0.0.0", 0))
                TempSock.settimeout(1)

                count = 0
                for count in range(0, 15):
                        try:
                                TempSock.sendto(x,(self.__host, 50000))
                                TempSock.recv(1000)
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

                if count == 14:
                        raise Exception('Reboot failed')

                print('Reboot complete')
                TempSock.close()

        def reboot_to_bootloader(self, wait_for_reboot=False):
                x = bytearray([0x01])
                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.sendto(x,(self.__host,50000))
                TempSock.close()

                if wait_for_reboot == False:
                        return

                # Wait two seconds for board to enter reset phase
                time.sleep(2)
                
                # Loop wait for reboot
                print('Waiting for board to reconnect...')
                x = bytearray([0x0])
                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.bind(("0.0.0.0", 0))
                TempSock.settimeout(1)

                count = 0
                for count in range(0, 15):
                        try:
                                TempSock.sendto(x,(self.__host, 50000))
                                TempSock.recv(1000)
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

                if count == 14:
                        raise Exception('Reboot failed')

                print('Reboot complete')
                TempSock.close()
