#!/bin/env python

import sys, zlib

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

def rep_scan_bits(value):
        return '{:056b}'.format(value)

def rep_vmon(value):
        return str(2.56 * float(value) / 65536.0)

class base:

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
                                # PROM ordering is reversed
                                self.__val.reverse()
                                return
                        # Assume SHA256 object
                        self.__val = val.__val

                def __int__(self):
                        x = 0
                        for i in range(0, 32):
                                x = x | (int(self.__val[31-i]) << 8 * i)
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
                        return s

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
                        if sys.version_info < (3,):
                                if (type(val) == int) or (type(val) == long):
                                        if val > (2**32)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        else:
                                if type(val) == int:
                                        if val > (2**32)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        self.__val = val.__val
                        
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
                        if sys.version_info < (3,):
                                if (type(val) == int) or (type(val) == long):
                                        if val > (2**16)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        else:
                                if type(val) == int:
                                        if val > (2**16)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        self.__val = val.__val

                def __int__(self):
                        return self.__val

                def __get__(self, objtype=None):
                        return self.__val

                def __set__(self, val):
                        return
        
                # Pretty output
                def __str__(self):
                        return str(self.__val)

        class NETWORK_INTERFACE(object):

                def __init__(self, val):
                        if type(val) == str:
                                val = int(val)
                        if type(val) == bytearray:
                                if len(val) != 1:
                                        raise Exception('Value is too large')
                                x = int(val[0])
                                val = x
                        if sys.version_info < (3,):
                                if (type(val) == int) or (type(val) == long):
                                        if val > 4:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        else:
                                if type(val) == int:
                                        if val > 4:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        self.__val = val.__val

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
                        if sys.version_info < (3,):
                                if (type(val) == int) or (type(val) == long):
                                        if val > (2**48)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        else:
                                if type(val) == int:
                                        if val > (2**48)-1:
                                                raise Exception('Value is too large')
                                        self.__val = val
                                        return
                        self.__val = val.__val

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

        def __init__(self, verbose, write_length, network_length, read_length, write_cfg, network_cfg, read_cfg):

                self.__verbose = verbose
                self.__WRITE_LENGTH = write_length
                self.__READ_LENGTH = read_length
                self.__NETWORK_LENGTH = network_length
                self.__network_cfg = network_cfg
                self.__write_cfg = write_cfg
                self.__read_cfg = read_cfg

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

        def get_network_keys(self):
                values = list()
                for key, value in self.__network_cfg.items():
                        values.append(key)
                return values

        def get_write_keys(self):
                values = list()
                for key, value in self.__write_cfg.items():
                        values.append(key)
                return values

        def get_read_keys(self):
                values = list()
                for key, value in self.__read_cfg.items():
                        values.append(key)
                return values        
                        
        def is_network_key(self, key):
                return key in self.__network_cfg

        def is_write_key(self, key):
                return key in self.__write_cfg

        def set_write_value(self, key, value):
                # Just pass the underlying integer if the default is integer
                if sys.version_info < (3,):
                        if (type(self.__write_cfg[key][2]) == int) or (type(self.__write_cfg[key][2]) == long):
                                if type(value) == int:
                                        self.__write_cfg[key][2] = value
                                elif type(value) == long:
                                        self.__write_cfg[key][2] = value
                                else:
                                        self.__write_cfg[key][2] = int(value, 0)
                                return
                else:
                        if type(self.__write_cfg[key][2]) == int:
                                if type(value) == int:
                                        self.__write_cfg[key][2] = value
                                else:
                                        self.__write_cfg[key][2] = int(value, 0)
                                return
                        
                self.__write_cfg[key][2] = type(self.__write_cfg[key][2])(value)
                
        def set_network_value(self, key, value):
                # Just pass the underlying integer if the default is integer
                if sys.version_info < (3,):
                        if (type(self.__network_cfg[key][2]) == int) or (type(self.__network_cfg[key][2]) == long):
                                self.__network_cfg[key][2] = int(value, 0)
                                return
                else:
                        if type(self.__network_cfg[key][2]) == int:
                                self.__network_cfg[key][2] = int(value, 0)
                                return

                self.__network_cfg[key][2] = type(self.__network_cfg[key][2])(value)

        def get_network_value(self, key):
                return self.__network_cfg[key][2]

        def get_network_size(self, key):
                return self.__network_cfg[key][1]

        def get_network_location(self, key):
                return self.__network_cfg[key][0]
        
        def get_write_value(self, key):
                return self.__write_cfg[key][2]

        def get_write_size(self, key):
                return self.__write_cfg[key][1]

        def get_write_location(self, key):
                return self.__write_cfg[key][0]
        
        def get_read_value(self, key):
                return self.__read_cfg[key][2]

        def get_read_size(self, key):
                return self.__read_cfg[key][1]

        def get_read_location(self, key):
                return self.__read_cfg[key][0]

        def print_network_cfg(self):
                for key, value in sorted(self.__network_cfg.items()):
                        if len(value) == 3:
                                print(key+' : '+str(value[2]))
                        else:
                                print(key+' : '+value[3](value[2]))

        def print_write_cfg(self):
                for key, value in sorted(self.__write_cfg.items()):
                        if len(value) == 3:
                                print(key+' : '+str(value[2]))
                        else:
                                print(key+' : '+value[3](value[2]))

        def print_read_cfg(self):
                for key, value in sorted(self.__read_cfg.items()):
                        if len(value) == 3:
                                print(key+' : '+str(value[2]))
                        else:
                                print(key+' : '+value[3](value[2]))
                                
        def __export_cfg_value(self, value):
                return int(value[2]) << value[0]

        def export_firmware_prom_data(self):

                result = bytearray(self.__WRITE_LENGTH)

                total = 0
                for key, value in self.__write_cfg.items():
                        x = self.__export_cfg_value(value)
                        total = total | x

                for i in range(0, self.__WRITE_LENGTH):
                        result[i] = total & 0xFF
                        total = total >> 8

                result.reverse()

                v = self.gen_checksum(result)
                result += v

                #for i in result:
                #        print(hex(i))                
                
                result += bytearray([0xFF]) * (256 - len(result))

                return result
        
        def export_network_prom_data(self):

                result = bytearray(self.__NETWORK_LENGTH)

                total = 0
                for key, value in self.__network_cfg.items():
                        x = self.__export_cfg_value(value)
                        total = total | x

                for i in range(0, self.__NETWORK_LENGTH):
                        result[i] = total & 0xFF
                        total = total >> 8

                result.reverse()

                v = self.gen_checksum(result)
                result += v
                result += bytearray([0xFF]) * (256 - len(result))
                
                return result

        def __import_cfg_value(self, key, target, data):
                value = target[key]
                start_point = int(value[0])
                bit_length = int(value[1])
                block = bytearray()

                #print key
                #print bit_length

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
                num_bytes = int(bit_length / 8)
                if (bit_length & 0x7) != 0:
                        num_bytes += 1

                # Just pass the underlying integer if the default is integer
                if sys.version_info < (3,):
                        if (type(target[key][2]) == int) or (type(target[key][2]) == long):
                                target[key][2] = myi
                                return
                else:
                        if type(target[key][2]) == int:
                                target[key][2] = myi
                                return

                # Otherwise pass a block
                for i in range(0, num_bytes):
                        block.append(myi & 0xFF)
                        myi = myi >> 8

                target[key][2] = type(target[key][2])(block)

        def import_firmware_prom_data(self, data):

                #for i in data:
                #        print(hex(i))                
                
                v = self.gen_checksum(data[0:self.__WRITE_LENGTH])

                if ( v != data[self.__WRITE_LENGTH:self.__WRITE_LENGTH+4] ):
                        # Invalid checksum
                        print('Imported firmware PROM data checksum is invalid, configuration will not be imported')
                        return False

                # Reverse so ordering matches VHDL
                rdata = data[0:self.__WRITE_LENGTH]
                rdata.reverse()

                for key, value in self.__write_cfg.items():
                        self.__import_cfg_value(key, self.__write_cfg, rdata[0:self.__WRITE_LENGTH])

                return True

        def import_network_prom_data(self, data):

                v = self.gen_checksum(data[0:self.__NETWORK_LENGTH])

                if ( v != data[self.__NETWORK_LENGTH:self.__NETWORK_LENGTH+4] ):
                        # Invalid checksum
                        print('Imported network PROM data checksum is invalid, configuration will not be imported')
                        return False

                # Reverse so ordering matches VHDL
                rdata = data[0:self.__NETWORK_LENGTH]
                rdata.reverse()

                for key, value in self.__network_cfg.items():
                        self.__import_cfg_value(key, self.__network_cfg, rdata[0:self.__NETWORK_LENGTH])

                return True
        
        def network_length(self):
                return self.__NETWORK_LENGTH
        def write_length(self):
                return self.__WRITE_LENGTH
        def read_length(self):
                return self.__READ_LENGTH
        def packet_receive_length(self):
                return (self.__READ_LENGTH + self.__WRITE_LENGTH + self.__NETWORK_LENGTH)

        def gen_checksum(self, data):

                # Used to be fletcher, now CRC32
                
                # Calculate CRC
                crc = zlib.crc32(data) & 0xFFFFFFFF

                # Copy data
                result = bytearray()
                
                # Append CRC
                for i in range(4):
                        byte = (crc >> (8*i)) & 0xFF
                        result.append(byte) #[len(data)+i] = byte

                return result
