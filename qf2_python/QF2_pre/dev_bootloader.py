#!/bin/env python

# Minor and major version matching
MAJOR_VERSION   = 0x00 # '?.xx+x'
MINOR_VERSION_1 = 0x07 # 'x.?x+x'
MINOR_VERSION_2 = 0x00 # 'x.x?+x'
MINOR_VERSION_3 = 0x04 # 'x.xx+?'

#from numpy import int32, int64, array, average
#import wave, pyaudio
#import matplotlib.pyplot as plt

from . import cfg as mycfg
from socket import *
from math import *
import string, time, sys, ctypes
from datetime import datetime, timedelta

# SD decode structures
class SD_SWITCH_FUNCTION_STATUS:

        offsets = {
                'MAX_CURRENT' : [496, 16],
                'SUPPORT_BITS_6' : [480, 16],
                'SUPPORT_BITS_5' : [464, 16],
                'SUPPORT_BITS_4' : [448, 16],
                'SUPPORT_BITS_3' : [432, 16],
                'SUPPORT_BITS_2' : [416, 16],
                'SUPPORT_BITS_1' : [400, 16],
                'FUNCTION_BITS_6' : [396, 4],
                'FUNCTION_BITS_5' : [392, 4],
                'FUNCTION_BITS_4' : [388, 4],
                'FUNCTION_BITS_3' : [384, 4],
                'FUNCTION_BITS_2' : [380, 4],
                'FUNCTION_BITS_1' : [376, 4],
                'DATA_STRUCTURE_VERSION' : [368, 8],
                'BUSY_STATUS_6' : [352, 16],
                'BUSY_STATUS_5' : [336, 16],
                'BUSY_STATUS_4' : [320, 16],
                'BUSY_STATUS_3' : [304, 16],
                'BUSY_STATUS_2' : [288, 16],
                'BUSY_STATUS_1' : [272, 16]
                }

        def bits_to_mask(self, bits):
                result = 0
                for i in range(0, bits):
                        result = (result << 1) | 1
                return result
        
        def decode(self, data):
                result = dict()

                for key, value in self.offsets.items():
                        result[key] = (data >> value[0]) & self.bits_to_mask(value[1])                                

                return result
        
class SD_CSD:

        offsets = {
                'CSD_STRUCTURE' : [126, 2],
                'TACC' : [112, 8],
                'NSAC' : [104, 8],
                'TRAN_SPEED' : [96, 8],
                'CCC' : [84, 12],
                'READ_BL_LEN' : [80, 4],
                'READ_BL_PARTIAL' : [79, 1],
                'WRITE_BLK_MISALIGN' : [78, 1],
                'READ_BLK_MISALIGN' : [77, 1],
                'DSR_IMP' : [76, 1],
                'C_SIZE' : [48, 22],
                'ERASE_BLK_EN' : [46, 1],
                'SECTOR_SIZE' : [39, 7],
                'WP_GRP_SIZE' : [32, 7],
                'WP_GRP_ENABLE' : [31, 1],
                'R2W_FACTOR' : [26, 3],
                'WRITE_BL_LEN' : [22, 4],
                'WRITE_BL_PARTIAL' : [21, 1],
                'FILE_FORMAT_GRP' : [15, 1],
                'COPY' : [14, 1],
                'PERM_WRITE_PROTECT' : [13, 1],
                'TMP_WRITE_PROTECT' : [12, 1],
                'FILE_FORMAT' : [10, 2]
                }

        def bits_to_mask(self, bits):
                result = 0
                for i in range(0, bits):
                        result = (result << 1) | 1
                return result
        
        def decode(self, data):
                result = dict()

                csd_type = (data >> 126) & 0x3

                if csd_type == 0:
                        raise Exception('Standard capacity SD cards (< 2GB) are not supported')
                elif csd_type == 1:
                        for key, value in self.offsets.items():
                                result[key] = (data >> value[0]) & self.bits_to_mask(value[1])                                
                else:
                        raise Exception('CSD structure unrecognized')

                return result

# Set this for a reasonable speed
morse_wpm_multiplier = 200
morse_inter_mark_gap = 1 * morse_wpm_multiplier
morse_short_mark = 1 * morse_wpm_multiplier
morse_long_mark = 3 * morse_wpm_multiplier
morse_letter_gap = 3 * morse_wpm_multiplier
morse_word_gap = 7 * morse_wpm_multiplier
morse_frequency = 50

morse_alphabet = {
        'a' : [0, 1],
        'b' : [1, 0, 0, 0],
        'c' : [1, 0, 1, 0],
        'd' : [1, 0, 0],
        'e' : [0],
        'f' : [0, 0, 1, 0],
        'g' : [1, 1, 0],
        'h' : [0, 0, 0, 0],
        'i' : [0, 0],
        'j' : [0, 1, 1, 1],
        'k' : [1, 0, 1],
        'l' : [0, 1, 0, 0],
        'm' : [1, 1],
        'n' : [1, 0],
        'o' : [1, 1, 1],
        'p' : [0, 1, 1, 0],
        'q' : [1, 1, 0, 1],
        'r' : [0, 1, 0],
        's' : [0, 0, 0],
        't' : [1],
        'u' : [0, 0, 1],
        'v' : [0, 0, 0, 1],
        'w' : [0, 1, 1],
        'x' : [1, 0, 0, 1],
        'y' : [1, 0, 1, 1],
        'z' : [1, 1, 0, 0],
        '1' : [0, 1, 1, 1, 1],
        '2' : [0, 0, 1, 1, 1],
        '3' : [0, 0, 0, 1, 1],
        '4' : [0, 0, 0, 0, 1],
        '5' : [0, 0, 0, 0, 0],
        '6' : [1, 0, 0, 0, 0],
        '7' : [1, 1, 0, 0, 0],
        '8' : [1, 1, 1, 0, 0],
        '9' : [1, 1, 1, 1, 0],
        '0' : [1, 1, 1, 1, 1],
        '.' : [0, 1, 0, 1, 0, 1],
        ',' : [1, 1, 0, 0, 1, 1],
        ':' : [1, 1, 1, 0, 0, 0],
        ';' : [1, 0, 1, 0, 1, 0],
        '?' : [0, 0, 1, 1, 0, 0],
        '!' : [1, 0, 1, 0, 1, 1],
        '\'' : [0, 1, 1, 1, 1, 0],
        '"' : [0, 1, 0, 0, 1, 0],
        '/' : [1, 0, 0, 1, 0],
        '(' : [1, 0, 1, 1, 0],
        ')' : [1, 0, 1, 1, 0, 1],
        '+' : [0, 1, 0, 1, 0],
        '-' : [1, 0, 0, 0, 0, 1],
        '=' : [1, 0, 0, 0, 1],
        '_' : [0, 0, 1, 1, 0, 1],
        '&' : [0, 1, 0, 0, 0],
        '@' : [0, 1, 1, 0, 1, 0],
        '$' : [0, 0, 0, 1, 0, 0, 1]
        }

class cfg(mycfg.base):

        def __init__(self, verbose):
                mycfg.base.__init__(self,
                                    verbose,
                                    self.__write_bytes,
                                    self.__network_bytes,
                                    self.__read_bytes,
                                    self.__write_cfg,
                                    self.__network_cfg,
                                    self.__read_cfg)

        __write_bytes = 24
        __network_bytes = 33
        __read_bytes = 100

        # Key : [Start (bits), Length (bits), Type / Default]
        __network_cfg = {

                'HIREL_IPV4_UNICAST_MAC' : [128+48+8+32, 48, mycfg.base.IPV4_MAC(0xAABBCCDDEEF1)],
                'HIREL_IPV4_UNICAST_IP' : [128+48+8, 32, mycfg.base.IPV4_IP(0xC0A80180)],                
                
                'NETWORK_INTERFACE' : [128+48, 8, mycfg.base.NETWORK_INTERFACE(0)],
                
                'IPV4_MULTICAST_MAC' : [128, 48, mycfg.base.IPV4_MAC(0)],
                'IPV4_MULTICAST_IP' : [96, 32, mycfg.base.IPV4_IP(0)],
                'IPV4_MULTICAST_PORT' : [80, 16, mycfg.base.IPV4_PORT(0)],
                
                'IPV4_UNICAST_MAC' : [32, 48, mycfg.base.IPV4_MAC(0xAABBCCDDEEF0)],
                'IPV4_UNICAST_IP' : [0, 32, mycfg.base.IPV4_IP(0xC0A8017F)]

        }

        # Key : [Start (bits), Length (bits), Type / Default]
        __write_cfg = {

                '__ICAP_WRITE_DATA' : [64, 16, int(0)],
                '__ICAP_ENABLE' : [59, 1, int(0)],
                '__ICAP_WRITE' : [58, 1, int(0)],
                '__ICAP_CE' : [57, 1, int(0)],
                '__ICAP_CLK' : [56, 1, int(0)],
                
                '__SD_DAT' : [50, 4, int(0)],
                '__SD_CMD' : [49, 1, int(0)],
                '__SD_CLK' : [48, 1, int(0)],

                '__SD_T_DAT' : [42, 4, int(0)],
                '__SD_T_CMD' : [41, 1, int(0)],
                '__SD_T_CLK' : [40, 1, int(0)],

                'FAN_PWM_GRADIENT' : [32, 8,  int(0x09)],
                'FAN_PWM_STOP_TEMPERATURE' : [24, 8,  int(0)],
                'FAN_PWM_MINIMUM_TEMPERATURE' : [16, 8,  int(0x28)],
                'FAN_PWM_MINIMUM_DUTY_CYCLE' : [8, 8,  int(0x4d)],

                '__N_TAS2505_RESET' : [7, 1, int(0)],
                'MONITORING_ENABLE' : [6, 1, int(0)],
                '__FLASH_READER_DISABLE' : [5, 1, int(0)],
                'AUTOBOOT_TO_RUNTIME' : [4, 1, int(0)],
                '__SYS_I2C_RESET' : [2, 1, int(1)],
                '__SYS_I2C_SDA' : [1, 1, int(1)],
                '__SYS_I2C_SCL' : [0, 1, int(1)]

        }
                                        
        # Key : [Start (bits), Length (bits), Type]
        __read_cfg = {

                '__ICAP_READ_DATA' : [98*8, 16, int()],
                
                '__SD_DAT' : [97*8+1, 4, int()],
                '__SD_CMD' : [97*8, 1, int()],

                '__LATCH_RNW' : [96*8+7, 1, int()],
                '__LATCH_R8N16' : [96*8+6, 1, int()],
                '__LATCH_D8N16' : [96*8+5, 1, int()],
                '__LATCH_SCL' : [96*8+2, 1, int()],
                '__LATCH_SDA' : [96*8+1, 1, int()],
                '__LATCH_SIR' : [96*8, 1, int()],
                '__LATCH_CHAIN' : [95*8, 8, int()],
                '__LATCH_SLAVE_ADDRESS' : [94*8, 8, int()],
                '__LATCH_READ_SLAVE_REGISTER' : [92*8, 16, int()],
                '__LATCH_WRITE_DATA' : [90*8, 16, int()],
                
                'FAN_PWM_CURRENT_DUTY_CYCLE' : [89*8, 8, int()],
                
                '__MDIO_EXTENDED_STATUS' : [87*8, 16, int()],
                '__MDIO_BASIC_STATUS' : [85*8, 16, int()],
                
                '__TAS2505_COUNT' : [80*8, 32, int()],
                
                'CONFIGURATION_DEFAULT' : [79*8, 1, int()],
                
                '__FLASH_READER_DATA_OUT_EMPTY' : [78*8+2, 1, int()],
                '__FLASH_READER_ERROR' : [78*8+1, 1, int()],
                '__FLASH_READER_DONE' : [78*8, 1, int()],
                
                '__ICAP_LAST_BOOT_DATA' : [77*8, 8, int()],

                '__CONTROLLER_SYS_I2C_READ_DATA' : [75*8, 16, int()],
                
                'I2C_ERROR_LATCH' : [74*8+7, 1, int()],
                'I2C_DONE_LATCH' : [74*8+6, 1, int()],
                'ATSHA204_ERROR' : [74*8+5, 1, int()],
                'ATSHA204_DONE' : [74*8+4, 1, int()],
                '__N_IS_QF2P' : [74*8+3, 1, int()],
                '__JACK_SENSE' : [74*8+2, 1, int()],
                '__SYS_I2C_SDA' : [74*8+1, 1, int()],
                '__SYS_I2C_SCL' : [74*8, 1, int()]
                
                # Left out monitoring for the minute
                
        }

class interface(cfg):

        def __init__(
                        self,
                        target,
                        verbose
        ):

                # Settings
                self.__target = target
                self.__port = 50001
                self.__i2c_port = 50002
                self.__audio_port = 50004
                self.__mic_port = 50005
                self.BOARD_UID = str()

                # Interface socket
                self.UDPSock = socket(AF_INET,SOCK_DGRAM)
                self.UDPSock.bind(("0.0.0.0", 0))
                self.UDPSock.settimeout(2)

                # External I2C socket
                self.I2CSock = socket(AF_INET, SOCK_DGRAM)
                self.I2CSock.bind(("0.0.0.0", 0))
                self.I2CSock.settimeout(2)

                # Audio socket
                self.AudioSock = socket(AF_INET,SOCK_DGRAM)
                self.AudioSock.bind(("0.0.0.0", 0))
                self.AudioSock.settimeout(2)

                # Microphone socket
                self.MicSock = socket(AF_INET,SOCK_DGRAM)
                self.MicSock.bind(("0.0.0.0", 0))
                self.MicSock.settimeout(2)
                
                # Initialize the configuration layer
                cfg.__init__(self, verbose)

                #raise Exception('This is an intentional exception - the bootloader interface is a placeholder for future use.')

        def sd_init(self):

                # Initialize the clock, release tristate
                self.set_byte(6, 0, 1)
                self.set_byte(5, 1, 1)

                # Clock 74 times
                for i in range(0, 74):
                        self.set_byte(6, 1, 1)
                        self.set_byte(6, 0, 1)

                # CMD0
                self.sd_cmd(0x4000000000)

                # CMD8
                self.sd_cmd_with_response(0x4800000100, 48)

                # IDLE -> RDY

                while True:

                        # CMD55
                        self.sd_cmd_with_response(0x7700000000, 48)
                        # ACMD41 (3.2-3.3V)
                        res = self.sd_cmd_with_response(0x6950FF8000, 48)

                        # Exit on busy
                        if ( (res>>39) & 1 ) == 1:
                                break

                        time.sleep(0.001)

                # CMD11 - don't expect result
                #self.sd_cmd(0x4B00000000)
                
                # RDY -> IDENT
                
                # CMD2
                self.sd_cmd_with_response(0x4200000000, 136)

                # IDENT -> STDBY
                
                # CMD3
                rca = self.sd_cmd_with_response(0x4300000000, 48)

                # Extract RCA
                rca = (rca >> 24) & 0xFFFF
                self.__sd_rca = rca
                
                # CMD9 (Read CSD)
                csd = self.sd_cmd_with_response((0x4900000000) | (rca << 16), 136)
                csd = SD_CSD().decode(csd)

                if csd['TRAN_SPEED'] == 0x32:
                        print('Transfer speed: 12.5MB/s')
                elif csd['TRAN_SPEED'] == 0x5A:
                        print('Transfer speed: 25MB/s')
                else:
                        raise Exception('Transfer speed unrecognized')                     
                        
                print('Capacity: '+'{0:.2f}'.format(csd['C_SIZE']*512.0/(1024.0*1024.0))+'GB')

                #for key, value in sorted(csd.items()):
                #        print key, value

                # CMD10 (Read CID)
                cid = self.sd_cmd_with_response((0x4A00000000) | (rca << 16), 136)

                # CMD7 (Go from standby to transfer state)
                self.sd_cmd_with_response((0x4700000000) | (rca << 16), 48)

                # If card is locked. require CMD42 before ACMD6 instead of CMD55...

                # Switch to 4-bit data mode
                # CMD55
                self.sd_cmd_with_response(0x7700000000 | (rca << 16), 48)
                # ACMD6 (Move to 4-bit data bus)
                self.sd_cmd_with_response(0x4600000002, 48)

                # Switch to high speed mode)
                self.sd_switch_to_hs_mode()

                # Read block 0 data
                self.sd_read_data(0)

                block = bytearray()
                for i in range(0, 512):
                        block.append(i&0xFF)
                        
                self.sd_write_data(0, block)
                
        def sd_switch_to_hs_mode(self):

                cmd = 0x4680FFFFF1 | (self.__sd_rca << 16)
                
                # Start
                self.sd_clk(0, None)
                self.sd_clk(1, None)

                # CMD is 38-bit
                for i in range(0, 38):
                        self.sd_clk(cmd >> (37-i), None)

                # CRC
                crc = self.sd_crc7(cmd)

                # CRC-7
                for i in range(0, 7):
                        self.sd_clk(crc >> (6-i), None)

                # End
                self.sd_clk(1, None)

                # Find start bit of result
                while self.sd_clk(None, None)[0] == 1:
                        continue

                # Get response
                response = 0
                data_header = 0
                data_start = False
                data_count = 0
                for i in range(0, 47):
                        cd = self.sd_clk(None, None)
                        response = (response << 1) | cd[0]
                        if ( data_start == False ):
                                if cd[1] == 0:
                                        data_start = True
                        else:
                                data_header = (data_header << 4) | cd[1]
                                data_count = data_count + 1
                        
                #print data_count
                #print

                while data_count != 128:
                        cd = self.sd_clk(None, None)                        
                        data_header = (data_header << 4) | cd[1]
                        data_count = data_count + 1

                crc = self.sd_crc16(data_header, 128)
                #for i in crc:
                #        print hex(i),
                #print

                crc_0 = 0
                crc_1 = 0
                crc_2 = 0
                crc_3 = 0

                for i in range(0, 16):
                        tmp = self.sd_clk(None, None)[1]
                        crc_0 = (crc_0 << 1) | (tmp & 1)
                        crc_1 = (crc_1 << 1) | ((tmp >> 1) & 1)
                        crc_2 = (crc_2 << 1) | ((tmp >> 2) & 1)
                        crc_3 = (crc_3 << 1) | ((tmp >> 3) & 1)

                #print hex(crc_0), hex(crc_1), hex(crc_2), hex(crc_3)
                #print

                if crc_0 != crc[0]:
                        raise Exception('CRC mismatch on SD DAT0')
                if crc_1 != crc[1]:
                        raise Exception('CRC mismatch on SD DAT1')
                if crc_2 != crc[2]:
                        raise Exception('CRC mismatch on SD DAT2')
                if crc_3 != crc[3]:
                        raise Exception('CRC mismatch on SD DAT3')

                # Final clock (should be 0xF)
                self.sd_clk(None, None)[1]
                        
                sfs = SD_SWITCH_FUNCTION_STATUS().decode(data_header)

                if sfs['FUNCTION_BITS_1'] != 1:
                        raise Exception('Could not switch to HS mode')
                
                # Clock 8 times
                for i in range(0, 8):
                        self.sd_clk(None, None)
                        
                return response

        def sd_write_data(self, address, data):

                if len(data) != 512:
                        raise Exception('Data size is incorrect (should be 512 bytes)')
                
                # CMD24
                cmd = 0x5800000000 | address
                
                # Start
                self.sd_clk(0, None)
                self.sd_clk(1, None)

                # CMD is 38-bit
                for i in range(0, 38):
                        self.sd_clk(cmd >> (37-i), None)

                # CRC
                crc = self.sd_crc7(cmd)

                # CRC-7
                for i in range(0, 7):
                        self.sd_clk(crc >> (6-i), None)

                # End
                self.sd_clk(1, None)

                # Find start bit of result
                while self.sd_clk(None, None)[0] == 1:
                        continue

                # Get response
                response = 0
                for i in range(0, 47):
                        cd = self.sd_clk(None, None)
                        response = (response << 1) | cd[0]

                print(hex(response))

                exit()

                block = int()
                for i in data:
                        block = (block << 4) | (i & 0xF)
                        block = (block << 4) | ((i>>4) & 0xF)
                
                crc = self.sd_crc16(data_header, 1024)
                for i in crc:
                        print(hex(i)),
                print

                crc_0 = 0
                crc_1 = 0
                crc_2 = 0
                crc_3 = 0

                for i in range(0, 16):
                        tmp = self.sd_clk(None, None)[1]
                        crc_0 = (crc_0 << 1) | (tmp & 1)
                        crc_1 = (crc_1 << 1) | ((tmp >> 1) & 1)
                        crc_2 = (crc_2 << 1) | ((tmp >> 2) & 1)
                        crc_3 = (crc_3 << 1) | ((tmp >> 3) & 1)

                print(hex(crc_0), hex(crc_1), hex(crc_2), hex(crc_3))
                print('')

                # Final clock (should be 0xF)
                self.sd_clk(None, None)[1]

                # Clock 8 times
                for i in range(0, 8):
                        self.sd_clk(None, None)
                        
        def sd_read_data(self, address):

                # CMD17
                cmd = 0x5100000000 | address
                
                # Start
                self.sd_clk(0, None)
                self.sd_clk(1, None)

                # CMD is 38-bit
                for i in range(0, 38):
                        self.sd_clk(cmd >> (37-i), None)

                # CRC
                crc = self.sd_crc7(cmd)

                # CRC-7
                for i in range(0, 7):
                        self.sd_clk(crc >> (6-i), None)

                # End
                self.sd_clk(1, None)

                # Find start bit of result
                while self.sd_clk(None, None)[0] == 1:
                        continue

                # Get response
                response = 0
                data_header = 0
                data_start = False
                data_count = 0
                for i in range(0, 47):
                        cd = self.sd_clk(None, None)
                        response = (response << 1) | cd[0]
                        if ( data_start == False ):
                                if cd[1] == 0:
                                        data_start = True
                        else:
                                data_header = (data_header << 4) | cd[1]
                                data_count = data_count + 1
                                #if cd[1] != 0:
                                #        print data_count, hex(cd[1])
                        
                while data_count != 1024:
                        cd = self.sd_clk(None, None)                        
                        data_header = (data_header << 4) | cd[1]
                        data_count = data_count + 1
                        #if cd[1] != 0:
                        #        print data_count, hex(cd[1])

                crc = self.sd_crc16(data_header, 1024)
                #for i in crc:
                #        print hex(i),
                #print

                crc_0 = 0
                crc_1 = 0
                crc_2 = 0
                crc_3 = 0

                for i in range(0, 16):
                        tmp = self.sd_clk(None, None)[1]
                        crc_0 = (crc_0 << 1) | (tmp & 1)
                        crc_1 = (crc_1 << 1) | ((tmp >> 1) & 1)
                        crc_2 = (crc_2 << 1) | ((tmp >> 2) & 1)
                        crc_3 = (crc_3 << 1) | ((tmp >> 3) & 1)

                if crc_0 != crc[0]:
                        raise Exception('CRC mismatch on SD DAT0')
                if crc_1 != crc[1]:
                        raise Exception('CRC mismatch on SD DAT1')
                if crc_2 != crc[2]:
                        raise Exception('CRC mismatch on SD DAT2')
                if crc_3 != crc[3]:
                        raise Exception('CRC mismatch on SD DAT3')
                        
                #print hex(crc_0), hex(crc_1), hex(crc_2), hex(crc_3)
                #print

                # Final clock (should be 0xF)
                self.sd_clk(None, None)[1]

                # Clock 8 times
                for i in range(0, 8):
                        self.sd_clk(None, None)
                        
                return response
                
        def sd_cmd(self, cmd):

                # Start
                self.sd_clk(0, None)
                self.sd_clk(1, None)

                # CMD is 38-bit
                for i in range(0, 38):
                        self.sd_clk(cmd >> (37-i), None)

                # CRC
                crc = self.sd_crc7(cmd)

                # CRC-7
                for i in range(0, 7):
                        self.sd_clk(crc >> (6-i), None)

                # End
                self.sd_clk(1, None)

                # Clock 8 times
                for i in range(0, 8):
                        self.sd_clk(None, None)

        def sd_cmd_with_response(self, cmd, rlen):

                # Start
                self.sd_clk(0, None)
                self.sd_clk(1, None)

                # CMD is 38-bit
                for i in range(0, 38):
                        self.sd_clk(cmd >> (37-i), None)

                # CRC
                crc = self.sd_crc7(cmd)

                # CRC-7
                for i in range(0, 7):
                        self.sd_clk(crc >> (6-i), None)

                # End
                self.sd_clk(1, None)

                # Find start bit of result
                while self.sd_clk(None, None)[0] == 1:
                        continue

                # Get result
                result = 0
                for i in range(0, rlen-1):
                        result = (result << 1) | self.sd_clk(None, None)[0]

                # Clock 8 times
                for i in range(0, 8):
                        self.sd_clk(None, None)
                        
                return result
                
        def sd_crc7(self, cmd):

                crc = 0
                
                for i in range(0, 40):
                        inv = ((cmd >> (39-i)) & 1) ^ ((crc >> 6) & 1)
                        crc = (((crc ^ (inv << 2)) << 1) | inv) & 0x7F

                return crc

        def sd_crc16(self, data, num_nibbles):

                # CRC16 is calculated per bus lane, so the calculation has to be split into four

                crc_0 = 0
                crc_1 = 0
                crc_2 = 0
                crc_3 = 0

                for i in range(0, num_nibbles):
                        
                        inv = ((data >> (num_nibbles*4-1-i*4)) & 1) ^ ((crc_3 >> 15) & 1)
                        crc_3 = (( ( crc_3 ^ ((inv << 4)|(inv << 11)) ) << 1) | inv) & 0xFFFF

                        inv = ((data >> (num_nibbles*4-2-i*4)) & 1) ^ ((crc_2 >> 15) & 1)
                        crc_2 = (( ( crc_2 ^ ((inv << 4)|(inv << 11)) ) << 1) | inv) & 0xFFFF

                        inv = ((data >> (num_nibbles*4-3-i*4)) & 1) ^ ((crc_1 >> 15) & 1)
                        crc_1 = (( ( crc_1 ^ ((inv << 4)|(inv << 11)) ) << 1) | inv) & 0xFFFF

                        inv = ((data >> (num_nibbles*4-4-i*4)) & 1) ^ ((crc_0 >> 15) & 1)
                        crc_0 = (( ( crc_0 ^ ((inv << 4)|(inv << 11)) ) << 1) | inv) & 0xFFFF
                        
                return [crc_0, crc_1, crc_2, crc_3]
        
        def sd_clk(self, cmd, dat):

                if cmd == None:
                        # Tristate cmd
                        self.set_byte(5, 0, 2)
                else:
                        # Set dat
                        self.set_byte(6, (cmd & 1) << 1, 2)
                        # Release tristate
                        self.set_byte(5, 2, 2)

                if dat == None:
                        # Tristate dat
                        self.set_byte(5, 0, 0x3C)
                else:
                        # Set dat
                        self.set_byte(6, (dat & 0xF) << 2, 0x3C)
                        # Release tristate
                        self.set_byte(5, 0x3C, 0x3C)

                # Clock
                self.set_byte(6, 1, 1)
                self.set_byte(6, 0, 1)

                self.import_network_data()
                return [self.get_read_value('__SD_CMD'),
                        self.get_read_value('__SD_DAT')]
                
        def icap_write(self, data):
                # enable, write, ce, clk

                # Initialize clk, ce & write
                self.set_byte(7, 0x6, 0x7)
                
                # Enable the ICAP debug interface
                self.set_byte(7, 0x8, 0x08)

                # Chip select, write
                # Write, then ce, to avoid abort
                self.set_byte(7, 0x0, 0x4)
                self.set_byte(7, 0x0, 0x2)

                # Synchronize
                for i in [0xFFFF, 0xFFFF, 0xAA99, 0x5566, 0x2000]:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 1, 1)
                        self.set_byte(7, 0, 1)
                
                # Write the block
                for i in data:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 1, 1)
                        self.set_byte(7, 0, 1)

                # Desync and two NOPs
                # Flushes the pipeline
                for i in [0x30A1, 0x000D, 0x2000, 0x2000]:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 1, 1)
                        self.set_byte(7, 0, 1)
                        
                # Deassert CE
                self.set_byte(7, 0x2, 0x2)
                self.set_byte(7, 1, 1)
                self.set_byte(7, 0, 1)
                        
                # Disable the ICAP debug interface
                self.set_byte(7, 0x0, 0x08)

        def icap_read(self, data):

                # Initialize clk, ce & write
                self.set_byte(7, 0x6, 0x7)
                
                # Enable the ICAP debug interface
                self.set_byte(7, 0x8, 0x08)

                # Chip select, write
                # Write, then ce, to avoid abort
                self.set_byte(7, 0x0, 0x4)
                self.set_byte(7, 0x0, 0x2)
                
                # Write the block
                for i in [0xFFFF, 0xFFFF, 0xAA99, 0x5566, 0x2000]:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 1, 1)
                        self.set_byte(7, 0, 1)

                # Write the read command
                self.set_byte(8, data & 0xFF, 0xFF)
                self.set_byte(9, (data >> 8) & 0xFF, 0xFF)
                self.set_byte(7, 1, 1)
                self.set_byte(7, 0, 1)

                for i in [0x2000, 0x2000, 0x2000, 0x2000]:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 1, 1)
                        self.set_byte(7, 0, 1)

                # Deassert ce (synchronous to clk)
                self.set_byte(7, 0x2, 0x2)
                self.set_byte(7, 1, 1)
                self.set_byte(7, 0, 1)
                        
                # Switch to read (synchronous to clk)
                self.set_byte(7, 0x4, 0x4)
                self.set_byte(7, 0, 0x2)
                self.set_byte(7, 1, 0x1)
                self.set_byte(7, 0, 0x1)

                # Clock once
                self.set_byte(7, 1, 0x1)
                self.set_byte(7, 0, 0x1)

                self.import_network_data()
                result = self.get_read_value('__ICAP_READ_DATA')

                # Raise chip select
                self.set_byte(7, 0x2, 0x2)
                self.set_byte(7, 1, 1)
                self.set_byte(7, 0, 1)
                        
                # Chip select, write
                # Write, then ce, to avoid abort
                self.set_byte(7, 0x0, 0x4)
                self.set_byte(7, 0x0, 0x2)

                # Desync
                for i in [0x30A1, 0x000D, 0x2000, 0x2000]:
                        self.set_byte(8, i & 0xFF, 0xFF)
                        self.set_byte(9, (i >> 8) & 0xFF, 0xFF)
                        self.set_byte(7, 0, 0x1)
                        self.set_byte(7, 0x1, 0x1)

                # Raise chip select
                self.set_byte(7, 0x2, 0x2)
                self.set_byte(7, 1, 1)
                self.set_byte(7, 0, 1)

                # Disable the ICAP debug interface
                self.set_byte(7, 0x0, 0x08)

                return result
                
        # Microphone development code
        def mic_demo(self, fname, length):

                # Collect microphone data
                print('This test will collect mic data, apply a 5th order CIC filter, then play back the sample on the laptop and store it as a file')
                
                # Discard first packets as the buffer needs to flush (it will be stuck full)
                
                print('Flushing buffer')
                while True:
                        # Send a short packet to trigger a microphone data dump
                        self.MicSock.sendto('0',(self.__target, self.__mic_port))
                        next_data = bytearray(self.MicSock.recv(1400))
                        #print len(next_data)
                        if len(next_data) < 512:
                                break

                # Collect ~5s of data
                data_collected = 0
                last_length = 0
                raw_mic_data = bytearray()
                while data_collected < (length * 44100 * 8):
                        
                        self.MicSock.sendto('0',(self.__target, self.__mic_port))
                        next_data = bytearray(self.MicSock.recv(1400))
                        #next_data.reverse()
                        s = str('\b' * last_length)
                        output = 'Buffer status: '+'{0:.2f}'.format(100.0 * float(len(next_data)) / 1024.0) + '%'
                        print(s+'\b'+output),
                        sys.stdout.flush()
                        last_length = len(output)+1
                        if not next_data:
                                print('No data received')

                        data_collected += len(next_data)
                        raw_mic_data += next_data

                print('')
                print('Audio buffer size: '+str(data_collected*8)+' bits')

                bit_mic_data = list()
                for i in raw_mic_data:
                        for j in range(0, 8):
                                bit_mic_data.append((i >> (7-j)) & 1)

                print('Applying 5th order CIC decimator (x64)')
                decimated = self.cic_decimator(bit_mic_data)

                print('Removing first samples (filter settling)')
                decimated = decimated[64:]

                av = average(decimated)
                print('Removing DC bias ('+str(av)+')')
                for i in range(0, len(decimated)):
                        decimated[i] = decimated[i] - av

                print('Normalizing gain')
                maximum = 0
                for i in decimated:
                        if i < 0:
                                if -i > maximum:
                                        maximum = -i
                        elif i > maximum:
                                maximum = i

                for i in range(0, len(decimated)):
                        decimated[i] = (decimated[i] * 32767) / maximum

                print('Plotting audio')
                plt.plot(decimated)
                plt.show()

                print('Playing back audio')

                p = pyaudio.PyAudio()
                for x in range(p.get_device_count()):
                        for y in [p.get_device_info_by_index(x)]:
                                print('\n'.join([y['name']]))

                stream = p.open(format=p.get_format_from_width(2),
                                channels=1,
                                rate=44100,
                                output=True)

                audio_data = bytearray()
                #                for i in decimated:
                #                        v = ctypes.c_ushort(i).value
                #                        audio_data.append(v & 0xFF)
                #                        audio_data.append(v >> 8)

                # Average four samples, effectively drop sample rate to 11.025kHz
                for i in range(0, len(decimated)/4):
                        av = (decimated[i*4] + decimated[i*4+1] + decimated[i*4+2] + decimated[i*4+3]) / 4
                        #av /= 256
                        #av *= 256
                        v = ctypes.c_ushort(av).value
                        audio_data.append(v & 0xFF)
                        audio_data.append(v >> 8)
                        audio_data.append(v & 0xFF)
                        audio_data.append(v >> 8)
                        audio_data.append(v & 0xFF)
                        audio_data.append(v >> 8)
                        audio_data.append(v & 0xFF)
                        audio_data.append(v >> 8)
                        
                audio_data = str(audio_data)

                posn = 0
                while (posn < len(audio_data)):
                        stream.write(audio_data[posn:posn+1000])
                        posn += 1000

                stream.stop_stream()
                stream.close()

                p.terminate()

                # Save data
                audio_data = bytearray()
                for i in decimated:
                        v = ctypes.c_ushort(i).value
                        audio_data.append(v & 0xFF)
                        audio_data.append(v >> 8)
                audio_data = str(audio_data)
                
                # Open file to store
                sample = wave.open(fname, 'wb')
                sample.setnchannels(1)
                sample.setframerate(44100)
                sample.setsampwidth(2)
                sample.writeframes(audio_data)
                sample.close()
                
        def cic_decimator(self, source, decimation_factor=64, order=5, ibits=1, obits=16):

                # Calculate the total number of bits used internally, and the output
                # shift and mask required.
                numbits = order * int(round(log(decimation_factor) / log(2))) + ibits
                outshift = numbits - obits
                outmask  = (1 << obits) - 1

                # If we need more than 64 bits, we can't do it...
                assert numbits <= 64

                # Create a numpy array with the source
                result = array(source, int64 if numbits > 32 else int32)

                #print result

                #exit()

                # Do the integration stages
                for i in range(order):
                        result.cumsum(out=result)

                # Decimate
                result = array(result[decimation_factor - 1 : : decimation_factor])

                # Do the comb stages.  Iterate backwards through the array,
                # because we use each value before we replace it.
                for i in range(order):
                        result[len(result) - 1 : 0 : -1] -= result[len(result) - 2 : : -1]

                # Normalize the output
                result >>= outshift
                result &= outmask
                return result

        # Speaker development code
        def tas2505_enable(self):
                self.set_byte(0, 0x80, 0x80)

        def tas2505_disable(self):
                self.set_byte(0, 0x0, 0x80)

        def tas2505_write(self, address, value):
                # Setting the chain to 0 selects the audio amplifier
                self.i2c_controller_write(0, 0x18, address, value)

        def tas2505_osc_frequency(self):
                self.import_network_data()
                # Value in MHz
                return float(self.get_read_value('__TAS2505_COUNT')) / 2000000.0

        def speech_out_test(self, message):

                offset = 0
                buf = bytearray()
                while offset < len(message):
                        if message[offset:offset+2] == 'ip':
                                file = 'ip.wav'
                                offset += 2
                        elif message[offset:offset+3] == 'mac':
                                file = 'mac.wav'
                                offset += 3
                        elif message[offset] == ' ':
                                buf += (bytearray([0]) * 5000)
                                offset += 1
                                continue
                        else:
                                file = message[offset]+'.wav'
                                offset += 1

                        sample = wave.open('audio/hq/'+file)
                        #if sample.getsampwidth() != 1:
                        #        raise Exception('Audio bit depth isn\'t 8-bit')
                        if sample.getcomptype() != 'NONE':
                                raise Exception('Audio compression isn\'t supported')
                        #if sample.getframerate() != 11025:
                        #        raise Exception('Audio sample rate isn\'t 11.025kHz')

                        buf += bytearray(sample.readframes(sample.getnframes()))

                # Upscale the data to 44.1kHz, 16-bit
                # Don't worry about fancy interpolation
                stream_data = list()

                # 8b, 11.025kHz
                #for i in buf:
                #        # Multiply up to 16-bit, signed
                #        av = (int(i) - 127)
                #        av = av << 8
                #        # Interpolate x4
                #        stream_data.append(av)
                #        stream_data.append(av)
                #        stream_data.append(av)
                #        stream_data.append(av)

                # 16b, 44.1kHz
                for i in range(0, len(buf) / 2):
                        channel = ctypes.c_short((int(buf[i*2+1]) << 8) + int(buf[i*2])).value
                        stream_data.append(channel)
                        
                # Convert to output format
                d = bytearray(len(stream_data)*2)
                for i in range(0, len(stream_data)):
                        d[i*2] = ctypes.c_ushort(stream_data[i]).value >> 8
                        d[1+i*2] = ctypes.c_ushort(stream_data[i]).value & 0xFF

                # Send the audio, continuous repeat
                audio_used = 0
                last_length = 0
                posn = 0
                while posn < len(d):
                        
                        # Hack to keep the buf roughly full, not really the correct way to approach this
                        if (audio_used > 200):
                                time.sleep(0.04)
                                audio_used = audio_used - 1
                        
                        self.AudioSock.sendto(d[posn:posn+1000],(self.__target, self.__audio_port))
                        audio_used = bytearray(self.AudioSock.recv(1000))[0]
                        s = str('\b' * last_length)
                        output = 'Buffer status: '+'{0:.2f}'.format(100.0 * float(audio_used) / 255.0) + '%'
                        print(s+'\b'+output),
                        sys.stdout.flush()
                        last_length = len(output)+1
                        if not audio_used:
                                print('No data received')

                        posn += 1000
                print
                        
                        
        def tas2505_audio_test(self, fname):
                
                sample = wave.open(fname)

                if sample.getsampwidth() != 2:
                        raise Exception('Audio bit depth isn\'t 16-bit')
                if sample.getcomptype() != 'NONE':
                        raise Exception('Audio compression isn\'t supported')
                if sample.getframerate() != 44100:
                        raise Exception('Audio sample rate isn\'t 44.1kHz')

                # Just copy entire audio sample into memory
                audio_data = bytearray(sample.readframes(sample.getnframes()))

                #audio_data = sample.readframes(sample.getnframes())

                #p = pyaudio.PyAudio()
                #for x in range(p.get_device_count()):
                #        for y in [p.get_device_info_by_index(x)]:
                #                print '\n'.join([y['name']])

                #stream = p.open(format=p.get_format_from_width(sample.getsampwidth()),
                #                channels=sample.getnchannels(),
                #                rate=sample.getframerate(),
                #                output=True)

                #posn = 0
                #while (posn < len(audio_data)):
                #        stream.write(audio_data[posn:posn+1000])
                #        posn += 1000

                #stream.stop_stream()
                #stream.close()

                #p.terminate()

                #exit()

                # Convert to 16-bit signed. If data is stereo, pre-mix it.
                merged_data = list()
                if sample.getnchannels() == 2:
                        for i in range(0, len(audio_data) / 4):
                                left = ctypes.c_short((int(audio_data[i*4+1]) << 8) + int(audio_data[i*4])).value
                                right = ctypes.c_short((int(audio_data[i*4+3]) << 8) + int(audio_data[i*4+2])).value
                                merged_data.append((left + right) / 2)
                else:
                        for i in range(0, len(audio_data) / 2):
                                channel = ctypes.c_short((int(audio_data[i*2+1]) << 8) + int(audio_data[i*2])).value
                                merged_data.append(channel)

                # Normalize the data
                maximum = 0
                for i in merged_data:
                        if i < 0:
                                if -i > maximum:
                                        maximum = -i
                        elif i > maximum:
                                maximum = i
                
                for i in range(0, len(merged_data)):
                        merged_data[i] = (merged_data[i] * 32767) / maximum

                coeff_table = list()

                # A4 (~440Hz) sine wave
                for i in range(0, 100):
                        coeff_table.append(int(32767.0 * sin(2.0 * pi * float(i) / 100.0)))
                
                # 500-sample audio block
                d = bytearray(len(merged_data)*2)
                posn = 0

                # Copy coefficients
                #for j in range(0, 5):
                #        for i in range(0, 100):
                #               d[1+i * 2 + j * 200] = ctypes.c_ushort(coeff_table[i]).value >> 8
                #               d[i * 2 + j * 200] = ctypes.c_ushort(coeff_table[i]).value & 0xFF

                for i in range(0, len(merged_data)):
                        d[i*2] = ctypes.c_ushort(merged_data[i]).value >> 8
                        d[1+i*2] = ctypes.c_ushort(merged_data[i]).value & 0xFF

                # Send the audio, continuous repeat
                audio_used = 0
                last_length = 0
                while True:
                        posn = 0
                        while posn < len(d):
                        
                                # Hack to keep the buffer roughly full, not really the correct way to approach this
                                if (audio_used > 200):
                                        time.sleep(0.04)
                                        audio_used = audio_used - 1
                        
                                self.AudioSock.sendto(d[posn:posn+1000],(self.__target, self.__audio_port))
                                audio_used = bytearray(self.AudioSock.recv(1000))[0]
                                s = str('\b' * last_length)
                                output = 'Buffer status: '+'{0:.2f}'.format(100.0 * float(audio_used) / 255.0) + '%'
                                print(s+'\b'+output),
                                sys.stdout.flush()
                                last_length = len(output)+1
                                if not audio_used:
                                        print('No data received')

                                posn += 1000
                print

        def morse_message_test(self, message):

                # Generate a sine wave
                coeff_table = list()
                for i in range(0, morse_frequency):
                        coeff_table.append(int(16535 * sin(2.0 * pi * float(i) / float(morse_frequency))) + int(4000.0 * sin(2.0 * pi * float(i) / float(morse_frequency / 3)))+ int(4000.0 * sin(2.0 * pi * float(i) / float(morse_frequency / 7))))

                # Generate the waveform in its entirety (could be done at runtime but this is just a demo)
                data = list()
                had_last_space = False
                for i in message:
                        if i == ' ':
                                if had_last_space == True:
                                        continue
                                had_last_space = True
                                # Add word gap
                                data += [0] * morse_frequency * morse_word_gap
                        else:
                                had_last_space = False
                                code = morse_alphabet[i]
                                for j in code:
                                        if j == 0:
                                                data += coeff_table * morse_short_mark
                                        elif j == 1:
                                                data += coeff_table * morse_long_mark
                                        # Add inter-mark gap
                                        data += [0] * morse_frequency * morse_inter_mark_gap
                                # Snip off last inter-mark gap
                                data = data[:-(morse_frequency * morse_inter_mark_gap)]
                                # Add letter gap
                                data += [0] * morse_frequency * morse_letter_gap
                                
                plt.plot(data[0:200])
                plt.show()

                #exit()

                # Output array
                d = bytearray()
                posn = 0

                for i in data:
                        d.append(ctypes.c_ushort(data[i]).value & 0xFF)
                        d.append(ctypes.c_ushort(data[i]).value >> 8)

                #for j in range(0, 5):
                #        for i in range(0, 100):
                #               d[1+i * 2 + j * 200] = ctypes.c_ushort(data[i]).value >> 8
                #               d[i * 2 + j * 200] = ctypes.c_ushort(data[i]).value & 0xFF

                # Send the audio, continuous repeat
                audio_used = 0
                last_length = 0
                while True:
                        posn = 0
                        while posn < len(d):
                        
                                # Hack to keep the buffer roughly full, not really the correct way to approach this
                                if (audio_used > 200):
                                        time.sleep(0.04)
                                        audio_used = audio_used - 1
                        
                                self.AudioSock.sendto(d[posn:posn+1000],(self.__target, self.__audio_port))
                                audio_used = bytearray(self.AudioSock.recv(1000))[0]
                                s = str('\b' * last_length)
                                output = 'Buffer status: '+'{0:.2f}'.format(100.0 * float(audio_used) / 255.0) + '%'
                                print(s+'\b'+output),
                                sys.stdout.flush()
                                last_length = len(output)+1
                                if not audio_used:
                                        print('No data received')

                                posn += 1000
                        break
                print
                
        def write_at24c32d_prom(self, prom_address, word_address, value):

                # GA is always zero now, so address is always 0x50
                if bottom_site == True:
                        self.i2c_controller_write(1, 0x50, word_address, value, False, True)
                else:
                        self.i2c_controller_write(4, 0x50, word_address, value, False, True)

                time.sleep(0.005)
                
                return

        def read_at24c32d_prom(self, word_address, bottom_site):

                # GA is always zero now, so address is always 0x50
                if bottom_site == True:
                        return self.i2c_controller_read(1, 0x50, word_address, False, True)
                else:
                        return self.i2c_controller_read(4, 0x50, word_address, False, True)

        def write_m24c02_prom(self, word_address, value, bottom_site):

                # GA is always zero now, so address is always 0x50
                if bottom_site == True:
                        self.i2c_controller_write(1, 0x50, word_address, value)
                else:
                        self.i2c_controller_write(4, 0x50, word_address, value)

                time.sleep(0.005)
                
                return

        def read_m24c02_prom(self, word_address, bottom_site):

                # GA is always zero now, so address is always 0x50
                if bottom_site == True:
                        return self.i2c_controller_read(1, 0x50, word_address)
                else:
                        return self.i2c_controller_read(4, 0x50, word_address)

        def i2c_controller_read(self, chain, address, register, data_16b=False, register_16b=False):
                
                # 7 byte command structure
                d = bytearray(7)

                # Mode bits
                if data_16b:
                        if register_16b:
                                d[0] = 0x1
                        else:
                                d[0] = 0x3
                else:
                        if register_16b:
                                d[0] = 0x5
                        else:
                                d[0] = 0x7

                d[1] = chain
                d[2] = address << 1
                d[3] = register & 0xFF
                d[4] = (register >> 8) & 0xFF
                d[5] = 0
                d[6] = 0

                # Send command
                read_bytes = str()

                try:
                        self.I2CSock.sendto(d,(self.__target, self.__i2c_port))
                        read_bytes = self.I2CSock.recv(1400)
                        if not read_bytes:
                                print('No data received')
                #        break
                except KeyboardInterrupt:
                        print('Ctrl-C detected')
                        exit(0)
                #except:
                #                continue

                res = bytearray(read_bytes)

                if res[0] == 0x02:
                        raise Exception('I2C acknowledge failed')

                if data_16b:
                        return ((int(res[2]) << 8) | int(res[1]))
                
                return int(res[1])

        def i2c_controller_write(self, chain, address, register, data, data_16b=False, register_16b=False, ignore_ack=False):
                
                # 7 byte command structure
                d = bytearray(7)

                # Mode bits
                if data_16b:
                        if register_16b:
                                d[0] = 0x0
                        else:
                                d[0] = 0x2
                else:
                        if register_16b:
                                d[0] = 0x4
                        else:
                                d[0] = 0x6

                d[1] = chain
                d[2] = address << 1
                d[3] = register & 0xFF
                d[4] = (register >> 8) & 0xFF
                d[5] = data & 0xFF
                d[6] = (data >> 8) & 0xFF

                # Send command
                read_bytes = str()

                #while True:
                try:
                        self.I2CSock.sendto(d,(self.__target, self.__i2c_port))
                        read_bytes = self.I2CSock.recv(1400)
                        if not read_bytes:
                                print('No data received')
                                #break
                except KeyboardInterrupt:
                        print('Ctrl-C detected')
                        exit(0)
                #        except:
                #                continue

                res = bytearray(read_bytes)

                if (res[0] == 0x02) and (ignore_ack == False):
                        raise Exception('I2C acknowledge failed')

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

#                while True:
                try:
                        self.UDPSock.sendto(rbytes,(self.__target, self.__port))
                        read_bytes = self.UDPSock.recv(cfg.packet_receive_length(self))
                        if not read_bytes:
                                print('No data received')
                        #break
                except KeyboardInterrupt:
                        print('Ctrl-C detected')
                        exit(0)
                        #except:
                        #        continue

                res = bytearray(read_bytes)
                res.reverse()
                return res

        def print_monitors(self):

                # TODO: Fix two's complement calculations
                # TODO: Check sense resistor values

                data = self.get_bytes()

                self.import_network_data()
                if ( self.get_write_value('MONITORING_ENABLE') == 0 ):
                        raise Exception('Monitoring is currently disabled - data unavailable (must set MONITORING_ENABLE=1).')                

                fan_duty_cycle = float(data[89])/2.55
                fan_speed = (int(data[73]) << 8) + int(data[72])

                z = []
                y = []
                x = []

                for i in range(0, 9):
                        if ( int(data[(i*4)+1+36]) & 0x80 != 0 ):
                                z.append(0.0)
                                z.append(0.0)
                        else:
                                z.append(((int(data[(i*4)+1+36]) << 8) + int(data[(i*4)+36])) * 0.0000025)
                                z.append(((int(data[(i*4)+3+36]) << 8) + int(data[(i*4)+2+36])) * 0.00125 * z[-1])

                for i in range(0, 8):
                        x.append(float(2.56 * float((int(data[(i*2)+1+4]) << 8) + int(data[(i*2)+4])) / 65536.0))
                        y.append(float(2.56 * float((int(data[(i*2)+1+20]) << 8) + int(data[(i*2)+20])) / 65536.0))

                board_temperature = float((int(data[3]) << 4) + (int(data[2]) >> 4)) + (float(int(data[2]) & 0xF) * 0.0625)
                kintex_temperature = float((int(data[1]) << 4) + (int(data[0]) >> 4)) + (float(int(data[0]) & 0xF) * 0.0625)

                print('')
                print('+12V:\t'+str(11.0 * y[0])+'V, '+str(z[16] / 0.004)+'A, '+str(z[17] / 0.004)+'W')
                print('')

                print('+3.3V_BOOT:\t'+str(2.0 * y[7])+'V, '+str(z[6] / 0.01)+'A, '+str(z[7] / 0.01)+'W')
                print('+1.2V_BOOT:\t'+str(y[1])+'V, '+str(z[14] / 0.01)+'A, '+str(z[15] / 0.01)+'W')
                print('')

                print('+1.0V_K7_VCCINT:\t'+str(y[3])+'V, '+str(z[8] / 0.004)+'A, '+str(z[9] / 0.004)+'W')
                print('+1.8V_K7_VCCAUX:\t'+str(y[2])+'V, '+str(z[10] / 0.01)+'A, '+str(z[11] / 0.01)+'W')
                print('K7_MGTAVTT:\t\t'+str(y[4])+'V')
                print('K7_MGTAVCC:\t\t'+str(y[5])+'V, '+str(z[12] / 0.01)+'A, '+str(z[13] / 0.01)+'W')
                print('K7_MGTAVCCAUX:\t\t'+str(y[6])+'V')
                print('+2.5V_K7_A;\t\t'+str(2.0 * x[6])+'V')
                print('+2.5V_K7_B:\t\t'+str(2.0 * x[7])+'V')
                print('+3.3V_MAIN:\t\t'+str(2.0 * x[5])+'V, '+str(z[0] / 0.004)+'A, '+str(z[1] / 0.004)+'W')
                print('')

                print('+12V_FMC:\t'+str(11.0 * x[2])+'V, '+str(z[2] / 0.01)+'A, '+str(z[3] / 0.01)+'W')
                print('+3.3V_FMC:\t'+str(2.0 * x[1])+'V')
                print('VADJ_FMC_TOP:\t'+str(2.0 * x[0])+'V')
                print('VADJ_FMC_BOT:\t'+str(x[3])+'V')
                print('VADJ SUPPLY:\t'+str(z[4] / 0.01)+'A, '+str(z[5] / 0.01)+'W')

                print('')
                print('LTM4628 temperature:\t'+str(150.0 - ((x[4] - 0.2) / 0.0023))+'C')
                print('Board temperature:\t'+str(board_temperature)+'C')
                print('Kintex-7 temperature:\t'+str(kintex_temperature)+'C')
                print('ATX fan tach:\t\t'+str(fan_speed*60)+' PPM')
                print('ATX fan duty cycle:\t'+str(fan_duty_cycle)+'%')
        
        def reboot_to_runtime(self, wait_for_reboot=False):
                x = bytearray([0x81])
                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.sendto(x,(self.__target,50000))
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
                                TempSock.sendto(x,(self.__target, 50000))
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
                TempSock.sendto(x,(self.__target,50000))
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
                                TempSock.sendto(x,(self.__target, 50000))
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

        def convToU64(self, v):
                if len(v) != 8:
                        raise Exception('Argument doesn\'t have 8 bytes')

                r = 0
                for i in range(0, 8):
                        r = (v[i] << (i*8)) | r

                return r

        def programControllerPMODA(self, f):
                p = self.__formatPMODControllerBinary(f)
                
                # Load the code
                TempSock = socket(AF_INET,SOCK_DGRAM)

                for i in p:
                        TempSock.sendto(bytearray(i),(self.__target, 50006))

        def programControllerPMODB(self, f):
                p = self.__formatPMODControllerBinary(f)
                
                # Load the code
                TempSock = socket(AF_INET,SOCK_DGRAM)

                for i in p:
                        TempSock.sendto(bytearray(i),(self.__target, 50007))
        
        def __formatPMODControllerBinary(self, f):
                
                with open(f, mode='rb') as f:
                        x = bytearray(f.read())

                        print(len(x))
                
                # Only Python3...
                #int.from_bytes(b, byteorder='big', signed=False)
                print(self.convToU64(x[0:8]))
                if self.convToU64(x[0:8]) != 28:
                        raise Exception('Binary PRAM data width is not 28')

                # Iterate through, ignoring first entry
                v = list()
                for i in range(0, (len(x)//8)-1):
                        v.append(self.convToU64(x[(i*8)+8:(i*8)+16]))

                if len(v) != 1024:
                        raise Exception('Binary code length isn\'t 1024 instructions')

                # Reformat the data into the loading format
                # Break programming data into packets, with a reset tag on the front of each one
                s = list()
                p = list()
                for i in v:
                        s.append((i>>24) & 0xF)
                        s.append((i>>16) & 0xFF)
                        s.append((i>>8) & 0xFF)
                        s.append(i & 0xFF)
                        if len(s) > 1000:
                                s.insert(0, 0x01)
                                p.append(s)
                                s = list()

                # Last bit
                if len(s) != 0:
                        s.insert(0, 0x01)
                        p.append(s)
                                
                # Release PMOD reset
                p.append([0])

                return p
        
        def sendReceiveControllerPMODA(self, data):

                data.insert(0, 0)

                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.bind(("0.0.0.0", 0))
                TempSock.settimeout(2)
                
                #read_bytes = str()

                try:
                        TempSock.sendto(bytearray(data),(self.__target, 50006))
                        read_bytes = TempSock.recv(1024)
                        if not read_bytes:
                                print('No data received')

                except KeyboardInterrupt:
                        print('Ctrl-C detected')
                        exit(0)

                res = bytearray(read_bytes)
                return res

        def sendReceiveControllerPMODB(self, data):

                data.insert(0, 0)

                TempSock = socket(AF_INET,SOCK_DGRAM)
                TempSock.bind(("0.0.0.0", 0))
                TempSock.settimeout(2)
                
                #read_bytes = str()

                try:
                        TempSock.sendto(bytearray(data),(self.__target, 50007))
                        read_bytes = TempSock.recv(1024)
                        if not read_bytes:
                                print('No data received')

                except KeyboardInterrupt:
                        print('Ctrl-C detected')
                        exit(0)

                res = bytearray(read_bytes)
                return res
        
