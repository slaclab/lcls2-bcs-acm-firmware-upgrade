#!/bin/env python

from socket import *
import string, time, sys, cfg as mycfg
from datetime import datetime, timedelta

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

        __write_bytes = 63
        __network_bytes = 22
        __read_bytes = 117+(23*3)

        # Key : [Start (bits), Length (bits), Type / Default]
        __network_cfg = {
                
                'IPV4_MULTICAST_MAC' : [128, 48, mycfg.base.IPV4_MAC(0)],
                'IPV4_MULTICAST_IP' : [96, 32, mycfg.base.IPV4_IP(0)],
                'IPV4_MULTICAST_PORT' : [80, 16, mycfg.base.IPV4_PORT(0)],

                'IPV4_UNICAST_MAC' : [32, 48, mycfg.base.IPV4_MAC(0xAABBCCDDEEFF)],
                'IPV4_UNICAST_IP' : [0, 32, mycfg.base.IPV4_IP(0xC0A8017F)]

        }

        # Key : [Start (bits), Length (bits), Type / Default]
        __write_cfg = {
                
                'KINTEX_BOOT_SHA256' : [248, 256, mycfg.base.SHA256('0000000000000000000000000000000000000000000000000000000000000000')],
                
                'FAN_PWM_GRADIENT' : [184, 8, int(9)],
                'FAN_PWM_STOP_TEMPERATURE' : [176, 8, int(0)],
                'FAN_PWM_MINIMUM_TEMPERATURE' : [168, 8, int(0x28)],
                'FAN_PWM_MINIMUM_DUTY_CYCLE' : [160, 8, int(0x4d)],
                
                'BOARD_SHUTDOWN_TEMPERATURE' : [152, 8, int(80)],
                'KINTEX_SHUTDOWN_TEMPERATURE' : [144, 8, int(80)],
                
                'SI57X_B_NEW_RFREQ' : [104, 38, int(0x02BBEAD49B)],
                'SI57X_B_NEW_N1' : [96, 7, int(3)],
                'SI57X_B_NEW_HSDIV' : [88, 3, int(0)],
                'SI57X_B_UPDATE' : [82, 1, int(1)],
                'SI57X_B_OE' : [81, 1, int(0)],
                'N_SI57X_B_CFG_ENABLE' : [80, 1, int(1)],
                
                'SI57X_A_NEW_RFREQ' : [40, 38, int(0x02BBEAD49B)],
                'SI57X_A_NEW_N1' : [32, 7, int(3)],
                'SI57X_A_NEW_HSDIV' : [24, 3, int(0)],
                'SI57X_A_UPDATE' : [18, 1, int(1)],
                'SI57X_A_OE' : [17, 1, int(0)],
                'N_SI57X_A_CFG_ENABLE' : [16, 1, int(1)],
                
                '__N_TAS_2505_RESET' : [11, 1, int(0)],
                'MONITORING_ENABLE' : [10, 1, int(0)],
                'MAIN_POWER_ENABLE' : [9, 1, int(0)],
                'POWER_BURST_MODE' : [8, 1, int(1)],
                
                '__SYS_I2C_RESET' : [2, 1, int(1)],
                '__SYS_I2C_SDA' : [1, 1, int(1)],
                '__SYS_I2C_SCL' : [0, 1, int(1)]

        }
                                        
        # Key : [Start (bits), Length (bits), Type]
        __read_cfg = {

                'SI57X_B_COUNT' : [608+(106*8), 32, int()],
                'SI57X_A_COUNT' : [608+(102*8), 32, int()],

                'MDIO_EXTENDED_STATUS' : [608+(100*8), 16, int()],
                'MDIO_BASIC_STATUS' : [608+(98*8), 16, int()],
                'FAN_PWM_CURRENT_DUTY_CYCLE' : [608+(97*8), 8, int()],
                
                '__TAS_COUNT' : [608+(93*8), 32, int()],
                
                '__CORRUPTED_BITSTREAM_TABLE' : [609+(92*8), 1, int()],
                '__CONFIGURATION_DEFAULT' : [608+(92*8), 1, int()],
                
                '__FLASH_READER_DATA_OUT_EMPTY' : [610+(91*8), 1, int()],
                '__FLASH_READER_ERROR' : [609+(91*8), 1, int()],
                '__FLASH_READER_DONE' : [608+(91*8), 1, int()],
                
                '__ATSHA204A_ERROR' : [613+(90*8), 1, int()],
                '__ATSHA204A_DONE' : [612+(90*8), 1, int()],
                'MAIN_POWER_STATE' : [611+(90*8), 1, int()],
                '__FAN_TACH' : [610+(90*8), 1, int()],
                '__N_IS_QF2_PRE' : [609+(90*8), 1, int()],
                '__JACK_SENSE' : [608+(90*8), 1, int()],
                
                'CONTROLLER_I2C_READ_DATA' : [608+(88*8), 16, int()],
                
                'I2C_ERROR_LATCH' : [615+(87*8), 1, int()],
                'I2C_DONE_LATCH' : [614+(87*8), 1, int()],
                'BOARD_OT_SHUTDOWN_LATCH' : [613+(87*8), 1, int()],
                'KINTEX_OT_SHUTDOWN_LATCH' : [612+(87*8), 1, int()],
                '__SYS_I2C_SDA' : [609+(87*8), 1, int()],
                '__SYS_I2C_SCL' : [608+(87*8), 1, int()],
                
                'SI57X_B_CURRENT_RFREQ' : [608+(82*8), 38, int()],
                'SI57X_B_CURRENT_N1' : [608+(81*8), 7, int()],
                'SI57X_B_CURRENT_HSDIV' : [608+(80*8), 3, int()],
                'SI57X_B_ERROR' : [609+(79*8), 1, int()],
                'SI57X_B_DONE' : [608+(79*8), 1, int()],
                
                'SI57X_A_CURRENT_RFREQ' : [608+(74*8), 38, int()],
                'SI57X_A_CURRENT_N1' : [608+(73*8), 7, int()],
                'SI57X_A_CURRENT_HSDIV' : [608+(72*8), 3, int()],
                'SI57X_A_ERROR' : [609+(71*8), 1, int()],
                'SI57X_A_DONE' : [608+(71*8), 1, int()],
                
                'FAN_SPEED' : [608+(69*8), 16, int()],
                
                'KINTEX_QSFP_2_RX1_POWER' : [608+(67*8), 16, int()],
                'KINTEX_QSFP_2_RX2_POWER' : [608+(65*8), 16, int()],
                'KINTEX_QSFP_2_RX3_POWER' : [608+(63*8), 16, int()],
                'KINTEX_QSFP_2_RX4_POWER' : [608+(61*8), 16, int()],
                'KINTEX_QSFP_2_TX1_BIAS' : [608+(59*8), 16, int()],
                'KINTEX_QSFP_2_TX2_BIAS' : [608+(57*8), 16, int()],
                'KINTEX_QSFP_2_TX3_BIAS' : [608+(55*8), 16, int()],
                'KINTEX_QSFP_2_TX4_BIAS' : [608+(53*8), 16, int()],
                
                'KINTEX_QSFP_2_VOLTAGE' : [608+(51*8), 16, int()],
                'KINTEX_QSFP_2_TEMPERATURE' : [608+(49*8), 16, int()],
                'KINTEX_QSFP_2_TX_FAULT' : [608+(48*8), 4, int()],
                'KINTEX_QSFP_2_LOS' : [608+(47*8), 8, int()],
                'KINTEX_QSFP_2_PRESENT' : [608+(46*8), 1, int()],
                
                'KINTEX_QSFP_1_RX1_POWER' : [608+(44*8), 16, int()],
                'KINTEX_QSFP_1_RX2_POWER' : [608+(42*8), 16, int()],
                'KINTEX_QSFP_1_RX3_POWER' : [608+(40*8), 16, int()],
                'KINTEX_QSFP_1_RX4_POWER' : [608+(38*8), 16, int()],
                'KINTEX_QSFP_1_TX1_BIAS' : [608+(36*8), 16, int()],
                'KINTEX_QSFP_1_TX2_BIAS' : [608+(34*8), 16, int()],
                'KINTEX_QSFP_1_TX3_BIAS' : [608+(32*8), 16, int()],
                'KINTEX_QSFP_1_TX4_BIAS' : [608+(30*8), 16, int()],
                
                'KINTEX_QSFP_1_VOLTAGE' : [608+(28*8), 16, int()],
                'KINTEX_QSFP_1_TEMPERATURE' : [608+(26*8), 16, int()],
                'KINTEX_QSFP_1_TX_FAULT' : [608+(25*8), 4, int()],
                'KINTEX_QSFP_1_LOS' : [608+(24*8), 8, int()],
                'KINTEX_QSFP_1_PRESENT' : [608+(23*8), 1, int()],
                
                'SPARTAN_QSFP_RX1_POWER' : [608+(21*8), 16, int()],
                'SPARTAN_QSFP_RX2_POWER' : [608+(19*8), 16, int()],
                'SPARTAN_QSFP_RX3_POWER' : [608+(17*8), 16, int()],
                'SPARTAN_QSFP_RX4_POWER' : [608+(15*8), 16, int()],
                'SPARTAN_QSFP_TX1_BIAS' : [608+(13*8), 16, int()],
                'SPARTAN_QSFP_TX2_BIAS' : [608+(11*8), 16, int()],
                'SPARTAN_QSFP_TX3_BIAS' : [608+(9*8), 16, int()],
                'SPARTAN_QSFP_TX4_BIAS' : [608+(7*8), 16, int()],
                
                'SPARTAN_QSFP_VOLTAGE' : [608+(5*8), 16, int()],
                'SPARTAN_QSFP_TEMPERATURE' : [608+(3*8), 16, int()],
                'SPARTAN_QSFP_TX_FAULT' : [608+(2*8), 4, int()],
                'SPARTAN_QSFP_LOS' : [608+(1*8), 8, int()],
                'SPARTAN_QSFP_PRESENT' : [608, 1, int()],
                
                'INA226_9_1' : [592, 16, int()],
                'INA226_8_1' : [576, 16, int()],
                'INA226_7_1' : [560, 16, int()],
                'INA226_6_1' : [544, 16, int()],
                'INA226_5_1' : [528, 16, int()],
                'INA226_4_1' : [512, 16, int()],
                'INA226_3_1' : [496, 16, int()],
                'INA226_2_1' : [480, 16, int()],
                'INA226_1_1' : [464, 16, int()],
                'INA226_0_1' : [448, 16, int()],
                'INA226_9_0' : [432, 16, int()],
                'INA226_8_0' : [416, 16, int()],
                'INA226_7_0' : [400, 16, int()],
                'INA226_6_0' : [384, 16, int()],
                'INA226_5_0' : [368, 16, int()],
                'INA226_4_0' : [352, 16, int()],
                'INA226_3_0' : [336, 16, int()],
                'INA226_2_0' : [320, 16, int()],
                'INA226_1_0' : [304, 16, int()],
                'INA226_0_0' : [288, 16, int()],
                
                'VMON_1_7' : [272, 16, int()],
                'VMON_1_6' : [256, 16, int()],
                'VMON_1_5' : [240, 16, int()],
                'VMON_1_4' : [224, 16, int()],
                'VMON_1_3' : [208, 16, int()],
                'VMON_1_2' : [192, 16, int()],
                'VMON_1_1' : [176, 16, int()],
                'VMON_1_0' : [160, 16, int()],
                'VMON_0_7' : [144, 16, int()],
                'VMON_0_6' : [128, 16, int()],
                'VMON_0_5' : [112, 16, int()],
                'VMON_0_4' : [96, 16, int()],
                'VMON_0_3' : [80, 16, int()],
                'VMON_0_2' : [64, 16, int()],
                'VMON_0_1' : [48, 16, int()],
                'VMON_0_0' : [32, 16, int()],
                
                'BOARD_TEMPERATURE' : [16, 16, int()],
                'KINTEX_TEMPERATURE' : [0, 16, int()]
                
        }
        
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

        def enable_monitoring(self):
                self.set_byte(1, 4, 4)
        def disable_monitoring(self):
                self.set_byte(1, 0, 4)

        def enable_main_power(self):
                self.set_byte(1, 2, 2)
        def disable_main_power(self):
                self.set_byte(1, 0, 2)

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

        def print_status(self):

                # Wait for system I2C controller to be inactive
                while True:
                        v = self.get_byte(3)
                        print('System I2C controller: ')
                        if v == 2:
                                print('ERROR')
                                break
                        elif v == 1:
                                print('IDLE')
                                break
                        else:
                                print('ACTIVE')
                        time.sleep(1)

        def main_3p3v_enable(self):
                self.pca9534_bit_set(0x2, 0, 6, True)

        def main_3p3v_disable(self):
                self.pca9534_bit_set(0x2, 0, 6, False)

        def fmc_vadj_enable(self):
                self.pca9534_bit_set(0x2, 0, 5, True)

        def fmc_vadj_disable(self):
                self.pca9534_bit_set(0x2, 0, 5, False)
                
        def fmc_3p3v_enable(self):
                self.pca9534_bit_set(0x2, 0, 4, True)

        def fmc_3p3v_disable(self):
                self.pca9534_bit_set(0x2, 0, 4, False)

        def fmc_12v_enable(self):
                self.pca9534_bit_set(0x2, 0, 0, True)

        def fmc_12v_disable(self):
                self.pca9534_bit_set(0x2, 0, 0, False)

        def kintex_vccint_enable(self):
                self.pca9534_bit_set(0x80, 0, 1, True)

        def kintex_vccint_disable(self):
                self.pca9534_bit_set(0x80, 0, 1, False)

        def kintex_1p0v_gtx_enable(self):
                self.pca9534_bit_set(0x80, 0, 0, True)

        def kintex_1p0v_gtx_disable(self):
                self.pca9534_bit_set(0x80, 0, 0, False)

        def kintex_1p2v_gtx_enable(self):
                self.pca9534_bit_set(0x80, 0, 7, True)

        def kintex_1p2v_gtx_disable(self):
                self.pca9534_bit_set(0x80, 0, 7, False)

        def get_port_expander_bit(self, chain, address, bit):
                return ((self.pca9534_read_input(chain, address) >> bit) & 0x1)

        def pca9534_bit_set(self, chain, address, bit, state = True):
                i = 1 << bit

                # Mask out to get the correct setting
                if state:
                        self.pca9534_write(chain, address, (self.pca9534_read_output(chain, address) & ~i) | i)
                else:
                        self.pca9534_write(chain, address, (self.pca9534_read_output(chain, address) & ~i))

                self.pca9534_direction_set(chain, address, (self.pca9534_direction_get(chain, address) & ~i))

        def pca9534_direction_set(self, chain, address, direction):
                self.i2c_controller_write(chain, 0x20 | address, PCA9534.DIRECTION, direction)
                return
                
        def pca9534_direction_get(self, chain, address):
                return self.i2c_controller_read(chain, 0x20 | address, PCA9534.DIRECTION)

        def pca9534_write(self, chain, address, value):
                self.i2c_controller_write(chain, 0x20 | address, PCA9534.OUTPUT, value)

        def pca9534_read_output(self, chain, address):
                return self.i2c_controller_read(chain, 0x20 | address, PCA9534.OUTPUT)

        def pca9534_read_input(self, chain, address):
                return self.i2c_controller_read(chain, 0x20 | address, PCA9534.INPUT)

        def set_top_fmc_vadj_resistor(self, value):
                self.max5387_write(0, 2, value)

        def set_bottom_fmc_vadj_resistor(self, value):
                self.max5387_write(0, 1, value)
               
        def atsha204_wake(self):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                addr_r = int('{:08b}'.format(0xC9)[::-1], 2)
                
                self.i2c_chain_set(0x8)

                self.i2c_start()
                time.sleep(0.001) # Wake
                self.i2c_stop()
                self.i2c_start()
                time.sleep(0.001) # Wake
                self.i2c_stop()

                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                l =  self.i2c_read()
                self.i2c_clk(1)
                self.i2c_stop()

                if l != 4:
                        raise Exception('Failed to wake ATSHA204A')

                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                l = self.i2c_read()
                self.i2c_clk(1)
                self.i2c_stop()

                if l != 0x11:
                        raise Exception('Failed to wake ATSHA204A')

                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                l = self.i2c_read()
                self.i2c_clk(1)
                self.i2c_stop()

                if l != 0x33:
                        raise Exception('Failed to wake ATSHA204A')

                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
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

                radd = int('{:08b}'.format(radd)[::-1], 2)

                self.i2c_chain_set(0x8)

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
                
                self.i2c_start()
                self.i2c_write(addr)
                self.i2c_check_ack()
                
                # wait texec (max) for read
                time.sleep(0.004)

                # Read (must be done by now)
                v = list()
                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                v.append(self.i2c_read())
                self.i2c_clk(1)
                self.i2c_stop()

                for i in range(1, v[0]):
                        self.i2c_start()
                        self.i2c_write(addr_r)
                        self.i2c_check_ack()
                        v.append(self.i2c_read())
                        self.i2c_clk(1)
                        self.i2c_stop()

                if (self.crc16_arc(v[0:-2]) != ((v[-1] << 8) | v[-2])):
                        raise Exception('CRC error reading ATSHA204A')

                # Put the device back to sleep
                self.atsha204_sleep()

                return v[1:5]

        def atsha204_random(self):
                addr = int('{:08b}'.format(0xC8)[::-1], 2)
                addr_r = int('{:08b}'.format(0xC9)[::-1], 2)
                word = int('{:08b}'.format(0x03)[::-1], 2)
                count = int('{:08b}'.format(0x07)[::-1], 2)
                cmd = int('{:08b}'.format(0x1B)[::-1], 2)

                crc = self.crc16_arc([0x07, 0x1B, 0x00, 0x00, 0x00])                
                crcl = int('{:08b}'.format(crc & 0xFF)[::-1], 2)
                crch = int('{:08b}'.format(crc >> 8)[::-1], 2)

                self.i2c_chain_set(0x8)
                self.atsha204_wake()

                self.i2c_start()
                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(word)
                self.i2c_check_ack()
                self.i2c_write(count) # count + crc(2) + opcode + param1 + param2(2)
                self.i2c_check_ack()
                self.i2c_write(cmd) # 0x1b
                self.i2c_check_ack()
                self.i2c_write(0) # param1
                self.i2c_check_ack()
                self.i2c_write(0) # param2
                self.i2c_check_ack()
                self.i2c_write(0) # param2
                self.i2c_check_ack()
                self.i2c_write(crcl) # crc lsb
                self.i2c_check_ack()
                self.i2c_write(crch) # crc msb
                self.i2c_check_ack()
                self.i2c_stop()
                
                # wait texec (max)
                time.sleep(0.1)

                # Read (must be done by now)
                self.i2c_start()
                self.i2c_write(addr_r)
                self.i2c_check_ack()
                l = self.i2c_read()
                self.i2c_clk(1)
                self.i2c_stop()
                
                for i in range(1, l):
                        self.i2c_start()
                        self.i2c_write(addr_r)
                        self.i2c_check_ack()
                        print(hex(self.i2c_read()))
                        self.i2c_clk(1)
                        self.i2c_stop()

                # Put the device back to sleep
                self.atsha204_sleep()
                
        def max5387_write(self, resistor, value):
                self.i2c_controller_write(0x2, 0x28, 0x10 | resistor, value)
                return

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

#
#       #def gtp_init(self):
#       #        self.write_bytes[1] = 0xE
#       #        self.send_receive()
#       #        self.write_bytes[1] = 0xC
#       #        self.send_receive()
#
#       #        time.sleep(1)
#
#       #        self.write_bytes[1] = 0x8
#       #        self.send_receive()
#       #        self.write_bytes[1] = 0
#       #        self.send_receive()
#
#       #def gtp_status(self):
#       #        self.send_receive()
#       #        print 'PLLs LOCKED:', hex(self.read_bytes[6] >> 4)
#       #        print 'RESET DONE:', hex(self.read_bytes[6] & 0xF)
#       #        print 'RX DATA CHECKER TRACKING:', hex(self.read_bytes[7] >> 4)
#       #        print 'RX BYTE IS ALIGNED:', hex(self.read_bytes[7] & 0xF)
#       #        print 'RX DATA ERROR COUNTS:', hex(self.read_bytes[140]), hex(self.read_bytes[139])
#
#       #        self.write_bytes[63] = 1
#       #        self.send_receive()
#       #        time.sleep(0.1)
#       #        self.write_bytes[63] = 0
#       #        self.send_receive()
#
#       #        print
#
#       #        for i in range(0, 16):
#       #                self.write_bytes[64] = i
#       #                self.send_receive()
#       #                self.send_receive()
#       #                print str(i) + ':', hex(self.read_bytes[145]), hex(self.read_bytes[144]), hex(self.read_bytes[143]), hex(self.read_bytes[142]), hex(self.read_bytes[141])


        def i2c_clk(self, bit):
                
                # Isolate reset bits with clock low and set data bit
                self.set_byte(0, ((bit & 1) << 1), 0x3)
                
                # Set clock high
                self.set_byte(0, 0x1, 0x1)

                # Sample bit
                result = int(self.get_byte(94) & 0x2) >> 1
               
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

        def kintex_qsfp_1_get(self):

                # Modsel the Kintex-7 QSFP1, disable the others
                self.pca9534_bit_set(0x80, 0, 2, True) # k7_1
                self.pca9534_bit_set(0x80, 0, 3, True) # k7_2
                self.pca9534_bit_set(0x80, 0, 4, True) # s6

                self.pca9534_bit_set(0x80, 0, 2, False) # k7_1

                # Chain is already set, query the QSFP
                return self.qsfp_get()

        def kintex_qsfp_2_get(self):

                # Modsel the Kintex-7 QSFP2, disable the others
                self.pca9534_bit_set(0x80, 0, 2, True) # k7_1
                self.pca9534_bit_set(0x80, 0, 3, True) # k7_2
                self.pca9534_bit_set(0x80, 0, 4, True) # s6

                self.pca9534_bit_set(0x80, 0, 3, False) # k7_2

                # Chain is already set, query the QSFP
                return self.qsfp_get()

        def spartan_qsfp_get(self):

                # Modsel the Spartan-6 QSFP, disable the others
                self.pca9534_bit_set(0x80, 0, 2, True) # k7_1
                self.pca9534_bit_set(0x80, 0, 3, True) # k7_2
                self.pca9534_bit_set(0x80, 0, 4, True) # s6

                self.pca9534_bit_set(0x80, 0, 4, False) # s6

                return self.qsfp_get()

        def qsfp_get(self):
                # Chain is already set, query the QSFP
                self.i2c_controller_write(0x80, 0x50, 128, 0)
                
                time.sleep(0.2)

                result = dict()
                x = self.i2c_controller_block_read(0x80, 0x50, 0, 128)
                for i in range(0, 128):
                        result[i] = x[i]
                x = self.i2c_controller_block_read(0x80, 0x50, 128, 128)
                for i in range(0, 128):
                        result[i+128] = x[i]

                # Lower memory
                result['IDENTIFIER'] = QSFP_INFO.IDENTIFIER.get(result[0], 'Unknown / unspecified')
                result['STATUS'] = QSFP_INFO.STATUS.get(result[2], 'Unknown / unspecified')
                for j in range(0, 4):
                        result['LOS RX' + str(j+1)] = '(' + str((result[3] >> j) & 1) + ')'
                        result['LOS TX' + str(j+1)] = '(' + str((result[3] >> j+4) & 1) + ')'
                        result['FAULT TX' + str(j+1)] = '(' + str((result[4] >> j) & 1) + ')'
                result['TEMPERATURE'] = str(float(conv_n((result[22] << 8) | result[23], 16)) / 256.0) + ' C'
                result['SUPPLY VOLTAGE'] = str(float((result[26] << 8) | result[27]) * 0.0001) + ' V'

                # Upper memory
                result['NOMINAL BIT RATE'] = str(float(result[140]) * 0.1) + ' Gb/s'
                result['SUPPORTED OM3 50um LENGTH'] = str(result[143] * 2) + ' m'
                output = str()
                for j in range(148, 164):
                        output += str(unichr(result[j]))
                result['VENDOR NAME'] = output
                result['IEEE COMPANY ID'] = '0x' + '{:06x}'.format(result[165] << 16 | result[166] << 8 | result[167])
                output = str()
                for j in range(168, 186):
                        output += str(unichr(result[j]))
                result['PART NUMBER'] = output
                result['REVISION LEVEL'] = str(unichr(result[184])) + str(unichr(result[185]))
                result['LASER WAVELENGTH'] = str(float((result[186] << 8) | result[187]) / 20.0) + ' nm'
                output = str()
                for j in range(196, 212):
                        output += str(unichr(result[j]))
                result['VENDOR SERIAL NUMBER'] = output

                return result

        def si57X_a_is_enabled(self):
                self.import_network_data()
                if ( self.get_write_value('SI57X_A_OE') == 1 ):
                        return True
                return False

        def si57X_b_is_enabled(self):
                self.import_network_data()
                if ( self.get_write_value('SI57X_B_OE') == 1 ):
                        return True
                return False
        
        def si57X_a_frequency(self):
                self.import_network_data()
                return 50000000.0 * float(2**24) / float(self.get_read_value('SI57X_A_COUNT'))

        def si57X_b_frequency(self):
                self.import_network_data()
                return 50000000.0 * float(2**24) / float(self.get_read_value('SI57X_B_COUNT'))

        def si57X_b_get_defaults(self):

                # Put SI57X_B controller in reset, with update low
                self.set_byte(10, 0x1, 0x5)

                # Release SI57X_A controller from reset
                self.set_byte(10, 0x0, 0x1)

                # Wait until done or error
                while True:
                        x = self.get_byte(155)
                        if x == 1:
                                break
                        if x == 2:
                                raise Exception('SI57X_B I2C error')

                # Read the data
                r = self.get_bytes()

                return {
                        'RFREQ' : (int(r[162]) << 32 |
                                   int(r[161]) << 24 |
                                   int(r[160]) << 16 |
                                   int(r[159]) << 8 |
                                   int(r[158])),
                        'N1' : int(r[157]),
                        'HSDIV' : int(r[156])
                        }


        def si57X_b_set(self, a):
                # Put SI57X_B controller in reset, with update high
                self.set_byte(10, 0x5, 0x5)
                
                # Load new settings
                self.set_byte(11, a['HSDIV'], 0xFF)
                self.set_byte(12, a['N1'], 0xFF)
                self.set_byte(13, a['RFREQ'] & 0xFF, 0xFF)
                self.set_byte(14, (a['RFREQ'] >> 8) & 0xFF, 0xFF)
                self.set_byte(15, (a['RFREQ'] >> 16) & 0xFF, 0xFF)
                self.set_byte(16, (a['RFREQ'] >> 24) & 0xFF, 0xFF)
                self.set_byte(17, (a['RFREQ'] >> 32) & 0xFF, 0xFF)

                # Release controller from reset
                self.set_byte(10, 0x0, 0x1)

                # Wait until done or error
                while True:
                        x = self.get_byte(155)
                        if x == 1:
                                break
                        if x == 2:
                                raise Exception('SI57X_A I2C error')

                # Verify the values
                # Read the data
                r = self.get_bytes()
                x = {
                        'RFREQ' : (int(r[162]) << 32 |
                                   int(r[161]) << 24 |
                                   int(r[160]) << 16 |
                                   int(r[159]) << 8 |
                                   int(r[158])),
                        'N1' : int(r[157]),
                        'HSDIV' : int(r[156])
                        }

                if x['HSDIV'] != a['HSDIV']:
                        raise Exception('SI57X_A frequency update failed')
                if x['N1'] != a['N1']:
                        raise Exception('SI57X_A frequency update failed')
                if x['RFREQ'] != a['RFREQ']:
                        raise Exception('SI57X_A frequency update failed')
        
        def si57X_a_get_defaults(self):

                # Put SI57X_A controller in reset, with update low
                self.set_byte(2, 0x1, 0x5)

                # Release SI57X_A controller from reset
                self.set_byte(2, 0x0, 0x1)

                # Wait until done or error
                while True:
                        x = self.get_byte(147)
                        if x == 1:
                                break
                        if x == 2:
                                raise Exception('SI57X_A I2C error')

                # Read the data
                r = self.get_bytes()

                return {
                        'RFREQ' : (int(r[154]) << 32 |
                                   int(r[153]) << 24 |
                                   int(r[152]) << 16 |
                                   int(r[151]) << 8 |
                                   int(r[150])),
                        'N1' : int(r[149]),
                        'HSDIV' : int(r[148])
                        }

        def si57X_a_set(self, a):
                # Put SI57X_A controller in reset, with update high
                self.set_byte(2, 0x5, 0x5)
                
                # Load new settings
                self.set_byte(3, a['HSDIV'], 0xFF)
                self.set_byte(4, a['N1'], 0xFF)
                self.set_byte(5, a['RFREQ'] & 0xFF, 0xFF)
                self.set_byte(6, (a['RFREQ'] >> 8) & 0xFF, 0xFF)
                self.set_byte(7, (a['RFREQ'] >> 16) & 0xFF, 0xFF)
                self.set_byte(8, (a['RFREQ'] >> 24) & 0xFF, 0xFF)
                self.set_byte(9, (a['RFREQ'] >> 32) & 0xFF, 0xFF)

                # Release controller from reset
                self.set_byte(2, 0x0, 0x1)

                # Wait until done or error
                while True:
                        x = self.get_byte(147)
                        if x == 1:
                                break
                        if x == 2:
                                raise Exception('SI57X_A I2C error')

                # Verify the values
                # Read the data
                r = self.get_bytes()
                x = {
                        'RFREQ' : (int(r[154]) << 32 |
                                   int(r[153]) << 24 |
                                   int(r[152]) << 16 |
                                   int(r[151]) << 8 |
                                   int(r[150])),
                        'N1' : int(r[149]),
                        'HSDIV' : int(r[148])
                        }

                if x['HSDIV'] != a['HSDIV']:
                        raise Exception('SI57X_A frequency update failed')
                if x['N1'] != a['N1']:
                        raise Exception('SI57X_A frequency update failed')
                if x['RFREQ'] != a['RFREQ']:
                        raise Exception('SI57X_A frequency update failed')

        def si57X_a_enable(self):
                self.set_byte(2, 0x2, 0x2)

        def si57X_a_disable(self):
                self.set_byte(2, 0x0, 0x2)

        def si57X_b_enable(self):
                self.set_byte(10, 0x2, 0x2)

        def si57X_b_disable(self):
                self.set_byte(10, 0x0, 0x2)

#               
#       def get_humidity(self):
#               command = 0xF5 # RH measure no I2C block
#               command = int('{:08b}'.format(command)[::-1], 2)
#
#               self.i2c_start()
#               self.i2c_write(0x1)
#               self.i2c_check_ack()
#               self.i2c_write(command)
#               self.i2c_check_ack()
#               self.i2c_stop()
#
#               time.sleep(0.00002)
#
#               self.i2c_start()
#               self.i2c_write(0x81)
#
#               while (not(self.i2c_check_ack(False))):
#                       self.i2c_stop()
#                       self.i2c_start()
#                       self.i2c_write(0x81)
#                       
#               res1 = self.i2c_read()
#               self.i2c_clk(0)
#               res2 = self.i2c_read()
#               self.i2c_clk(0)
#               res3 = self.i2c_read()
#               self.i2c_clk(1)
#               self.i2c_stop()
#
#               print hex(res1), hex(res2), hex(res3)
#
#               humidity = -6.0 + (125.0 * float(res1 * 256 + (res2 & 0xFC)) / 65536.0)
#               print humidity
#

        def write_8b_adc128d818(self, chain, address, value):
                addr = (0x1D << 1)
                addr_r = (0x1D << 1) | 1
                addr = int('{:08b}'.format(addr)[::-1], 2)
                addr_r = int('{:08b}'.format(addr_r)[::-1], 2)
                w = int('{:08b}'.format((address) & 0xFF)[::-1], 2)
                v = int('{:08b}'.format((value) & 0xFF)[::-1], 2)

                self.i2c_chain_set(chain)

                self.i2c_start()

                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(w)
                self.i2c_check_ack()
                self.i2c_write(v)
                self.i2c_check_ack()

                self.i2c_stop()             

        def read_8b_adc128d818(self, chain, address):
                addr = (0x1D << 1)
                addr_r = (0x1D << 1) | 1
                addr = int('{:08b}'.format(addr)[::-1], 2)
                addr_r = int('{:08b}'.format(addr_r)[::-1], 2)
                w = int('{:08b}'.format((address) & 0xFF)[::-1], 2)

                self.i2c_chain_set(chain)

                self.i2c_start()

                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(w)
                self.i2c_check_ack()
                
                self.i2c_repeated_start()

                self.i2c_write(addr_r)
                self.i2c_check_ack()
                result = self.i2c_read()
                self.i2c_clk(1)

                self.i2c_stop()             

                return result

        def read_16b_adc128d818(self, chain, address):
                addr = (0x1D << 1)
                addr_r = (0x1D << 1) | 1
                addr = int('{:08b}'.format(addr)[::-1], 2)
                addr_r = int('{:08b}'.format(addr_r)[::-1], 2)
                w = int('{:08b}'.format((address) & 0xFF)[::-1], 2)

                self.i2c_chain_set(chain)

                self.i2c_start()

                self.i2c_write(addr)
                self.i2c_check_ack()
                self.i2c_write(w)
                self.i2c_check_ack()
                
                self.i2c_repeated_start()

                self.i2c_write(addr_r)
                self.i2c_check_ack()
                result = self.i2c_read()
                self.i2c_clk(0)
                result = (result << 8) | self.i2c_read()
                self.i2c_clk(1)

                self.i2c_stop()             

                return (2.56 * float(result) / 65536.0)

        def read_adc128d818_values(self, chain):
                
                #print self.read_8b_adc128d818(chain, 0x3E) # Manufacturer ID (0x1)
                #print self.read_8b_adc128d818(chain, 0x3F) # Revision ID (0x9)

                # Check device ready
                while True:
                        if self.i2c_controller_read(chain, 0x1D, 0xC) == 0:
                                break
                        time.sleep(0.01)

                #self.write_8b_adc128d818(chain, 0xB, 2) # Advanced configuration
                self.i2c_controller_write(chain, 0x1D, 0xB, 2)

                #self.write_8b_adc128d818(chain, 0x9, 1) # One-shot
                self.i2c_controller_write(chain, 0x1D, 0x9, 1)
                
                # Check device ready
                while True:
                        #if self.read_8b_adc128d818(chain, 0xC) == 0:
                        #        break
                        if self.i2c_controller_read(chain, 0x1D, 0xC) == 0:
                                break
                        time.sleep(0.01)

                results = list()
                for i in range(0x20, 0x28):
                        results.append(2.56 * float(self.i2c_controller_read(chain, 0x1D, i, True)) / 65536.0)
                        #results.append(self.read_16b_adc128d818(chain, i))

                return results

        def write_16b_ina226(self, chain, device, address, value):
                d = int('{:08b}'.format((0x40 | device) << 1)[::-1], 2)
                a = int('{:08b}'.format((address) & 0xFF)[::-1], 2)
                msb = int('{:08b}'.format((value >> 8) & 0xFF)[::-1], 2)
                lsb = int('{:08b}'.format(value & 0xFF)[::-1], 2)

                self.i2c_chain_set(chain)

                self.i2c_start()

                self.i2c_write(d)
                self.i2c_check_ack()
                self.i2c_write(a)
                self.i2c_check_ack()
                self.i2c_write(msb)
                self.i2c_check_ack()
                self.i2c_write(lsb)
                self.i2c_check_ack()

                self.i2c_stop()             

        def read_16b_ina226(self, chain, device, address):
                d = int('{:08b}'.format((0x40 | device) << 1)[::-1], 2)
                d_r = int('{:08b}'.format(((0x40 | device) << 1) | 1)[::-1], 2)
                a = int('{:08b}'.format((address) & 0xFF)[::-1], 2)

                self.i2c_chain_set(chain)

                self.i2c_start()

                self.i2c_write(d)
                self.i2c_check_ack()
                self.i2c_write(a)
                self.i2c_check_ack()

                self.i2c_repeated_start()

                self.i2c_write(d_r)
                self.i2c_check_ack()
                result = self.i2c_read()
                self.i2c_clk(0)
                result = (result << 8) | self.i2c_read()
                self.i2c_clk(1)

                self.i2c_stop()             

                return result

        def read_ina226_values(self):

                # Chip IDs
                #print hex(self.read_16b_ina226(0x2, 0, 0xFE)) # +3.3V_MAIN
                ##print hex(self.read_16b_ina226(0x2, 1, 0xFE)) # +3.3V_FMC
                ##print hex(self.read_16b_ina226(0x2, 2, 0xFE)) # +12V_FMC
                ##print hex(self.read_16b_ina226(0x2, 3, 0xFE)) # VADJ
                ##print hex(self.read_16b_ina226(0x40, 0, 0xFE)) # +3.3V_BOOT
                ##print hex(self.read_16b_ina226(0x40, 1, 0xFE)) # +1.0V_K7_VCCINT
                ##print hex(self.read_16b_ina226(0x40, 2, 0xFE)) # +1.8V_K7_VCCAUX
                ##print hex(self.read_16b_ina226(0x40, 3, 0xFE)) # +1.0V_K7_GTX
                ##print hex(self.read_16b_ina226(0x40, 4, 0xFE)) # +1.2V_BOOT
                ##print hex(self.read_16b_ina226(0x40, 5, 0xFE)) # +12V

                # Bus voltages
                #for i in range(0, 4):
                #        print  float(self.read_16b_ina226(0x2, i, 0x2)) * 0.00125
                #for i in range(0, 6):
                #        print float(self.read_16b_ina226(0x40, i, 0x2)) * 0.00125

                # Change to average of 64 samples

                results = list()
                for i in range(0, 4):
                        self.i2c_controller_write(0x2, 0x40|i, 0x0, 0x4727, True)
                        print 'a'
                        r = self.i2c_controller_read(0x2, 0x40|i, 0x1, True)
                        print 'b'
                        if ( r & 0x8000 != 0 ):
                                results.append(0.0)
                                results.append(0.0)
                        else:
                                results.append(float(self.i2c_controller_read(0x2, 0x40|i, 0x1, True)) * 0.0000025)
                                results.append(float(self.i2c_controller_read(0x2, 0x40|i, 0x2, True)) * 0.00125 * results[-1])
                                
                for i in range(0, 6):
                        print 'c'
                        self.write_16b_ina226(0x40, 0x40|i, 0x0, 0x4727)
                        r = self.i2c_controller_read(0x40, 0x40|i, 0x1, True)
                        if ( r & 0x8000 != 0 ):
                                results.append(0.0)
                                results.append(0.0)
                        else:
                                results.append(float(self.i2c_controller_read(0x40, 0x40|i, 0x1, True)) * 0.0000025)
                                results.append(float(self.i2c_controller_read(0x40, 0x40|i, 0x2, True)) * 0.00125 * results[-1])

                return results

        def i2c_controller_block_read(self, chain, address, register_base, num_times, data_16b=False, register_16b=False):
                if num_times > 128:
                        raise Exception('num_times is too large ('+str(num_times)+')')

                results = list()
                v = bytearray()

                for i in range(0, num_times):

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
                        d[3] = (register_base+i) & 0xFF
                        d[4] = ((register_base+i) >> 8) & 0xFF
                        d[5] = 0
                        d[6] = 0

                        v = v + d

                # Send command
                read_bytes = str()

                while True:
                        try:
                                self.I2CSock.sendto(str(v),(self.__host, self.__i2c_port))
                                read_bytes = self.I2CSock.recv(1400)
                                if not read_bytes:
                                        print('No data received')
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

                res = bytearray(read_bytes)

                for i in range(0, num_times):
                        if res[i*3] == 0x2:
                                raise Exception('I2C acknowledge failed')
                        
                        if data_16b:
                                results.append((int(res[(i*3)+2]) << 8) | int(res[(i*3)+1]))
                        else:
                                results.append(int(res[(i*3)+1]))

                return results

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

                #for i in d:
                #        print hex(i)

                # Send command
                read_bytes = str()

                while True:
                        try:
                                self.I2CSock.sendto(str(d),(self.__host, self.__i2c_port))
                                read_bytes = self.I2CSock.recv(1400)
                                if not read_bytes:
                                        print('No data received')
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

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

                while True:
                        try:
                                self.I2CSock.sendto(str(d),(self.__host, self.__i2c_port))
                                read_bytes = self.I2CSock.recv(1400)
                                if not read_bytes:
                                        print('No data received')
                                break
                        except KeyboardInterrupt:
                                print('Ctrl-C detected')
                                exit(0)
                        except:
                                continue

                res = bytearray(read_bytes)

                if (res[0] == 0x02) and (ignore_ack == False):
                        raise Exception('I2C acknowledge failed')

        def print_monitors(self):

                # TODO: Fix two's complement calculations
                # TODO: Check sense resistor values
                # TODO: Tach reading issue

                # Get the monitoring data
                self.import_network_data()

                if ( self.get_write_value('MONITORING_ENABLE') == 0 ):
                        raise Exception('Monitoring is currently disabled - data unavailable (must set MONITORING_ENABLE=1).')
                        
                #headphone_jack_sense = self.get_read_value('__JACK_SENSE')
                #is_qf2_pre = ((int(data[118] >> 1) & 1) ^ 1)
                #fan_tach = int(data[118] >> 2) & 1
                #power_state = int(data[118] >> 3) & 1
                #i2c_error_latch = int(data[115] >> 7) & 1
                #i2c_done_latch = int(data[115] >> 6) & 1
                #board_ot_shutdown_latch = int(data[115] >> 5) & 1
                #kintex_ot_shutdown_latch = int(data[115] >> 4) & 1

                print
                print('Is QF2-pre:\t\t\t'+str(self.get_read_value('__N_IS_QF2_PRE') ^ 1))
                print('Headphone jack present:\t\t'+str(self.get_read_value('__JACK_SENSE')))
                print('Fan tach:\t\t\t'+str(self.get_read_value('__FAN_TACH')))
                print('Main power state:\t\t'+str(self.get_read_value('MAIN_POWER_STATE')))
                print('I2C done latch:\t\t\t'+str(self.get_read_value('I2C_DONE_LATCH')))
                print('I2C error latch:\t\t'+str(self.get_read_value('I2C_ERROR_LATCH')))
                print('Board OT shutdown latch:\t'+str(self.get_read_value('BOARD_OT_SHUTDOWN_LATCH')))
                print('Kintex OT shutdown latch:\t'+str(self.get_read_value('KINTEX_OT_SHUTDOWN_LATCH')))

                z = []
                y = []
                x = []

                if ( self.get_read_value('INA226_0_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_0_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_0_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_1_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_1_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_1_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_2_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_2_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_2_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_3_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_3_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_3_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_4_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_4_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_4_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_5_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_5_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_5_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_6_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_6_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_6_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_7_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_7_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_7_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_8_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_8_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_8_1') * 0.00125 * z[-1])

                if ( self.get_read_value('INA226_9_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.get_read_value('INA226_9_0') * 0.0000025)
                        z.append(self.get_read_value('INA226_9_1') * 0.00125 * z[-1])

                x.append(float(2.56 * float(self.get_read_value('VMON_0_0')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_1')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_2')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_3')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_4')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_5')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_6')) / 65536.0))
                x.append(float(2.56 * float(self.get_read_value('VMON_0_7')) / 65536.0))

                y.append(float(2.56 * float(self.get_read_value('VMON_1_0')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_1')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_2')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_3')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_4')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_5')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_6')) / 65536.0))
                y.append(float(2.56 * float(self.get_read_value('VMON_1_7')) / 65536.0))

                boot_1p2v = y[1]
                k7_vccaux = y[2]
                k7_vccint = y[3]
                k7_mgtavtt = y[4]
                k7_mgtavcc = y[5]
                k7_mgtavccaux = y[6]
                boot_3p3v = 2.0 * y[7]

                main_3p3v = 2.0 * x[5]
                k7_a_2p5v = 2.0 * x[6]
                k7_b_2p5v = 2.0 * x[7]

                vadj_fmc_top = 2.0 * x[0]
                vadj_fmc_bot = x[3]

                print('')
                print('+12V:\t\t\t'+'{0:.3f}'.format(11.0 * y[0])+'\tV\t'+'{0:.3f}'.format(z[18] / 0.004)+'\tA\t'+'{0:.3f}'.format(z[19] / 0.004)+'\tW')
                print('')

                s = '+3.3V_BOOT:\t\t' + '{0:.3f}'.format(boot_3p3v) + '\tV\t' + '{0:.3f}'.format(z[8] / 0.01) + '\tA\t' + '{0:.3f}'.format(z[9] / 0.01)+'\tW'
                if ( (boot_3p3v > (3.3 * 1.03)) or (boot_3p3v < (3.3 * 0.97)) ):
                        s = '!!!!! ' + s
                print (s)

                s = '+1.2V_BOOT:\t\t' + '{0:.3f}'.format(boot_1p2v) + '\tV\t' + '{0:.3f}'.format(z[16] / 0.01) + '\tA\t' + '{0:.3f}'.format(z[17] / 0.01) + '\tW'
                if ( (boot_1p2v > (1.2 * 1.03)) or (boot_1p2v < (1.2 * 0.97)) ):
                        s  = '!!!!! ' + s
                print(s)

                print('')

                s = '+1.0V_K7_VCCINT:\t' + '{0:.3f}'.format(k7_vccint) + '\tV\t' + '{0:.3f}'.format(z[10] / 0.004)+'\tA\t' + '{0:.3f}'.format(z[11] / 0.004)+'\tW'
                if ( (k7_vccint > 1.03) or (k7_vccint < 0.97) ):
                        s  = '!!!!! ' + s
                print(s)

                s = '+1.8V_K7_VCCAUX:\t' + '{0:.3f}'.format(k7_vccaux)+'\tV\t' + '{0:.3f}'.format(z[12] / 0.01) + '\tA\t' + '{0:.3f}'.format(z[13] / 0.01)+'\tW'
                if ( (k7_vccaux > (1.8 * 1.03)) or (k7_vccaux < (1.8 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)
                        
                s = 'K7_MGTAVTT:\t\t' + '{0:.3f}'.format(k7_mgtavtt) + '\tV'
                if ( (k7_mgtavtt > (1.2 * 1.03)) or (k7_mgtavtt < (1.2 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                s = 'K7_MGTAVCC:\t\t' + '{0:.3f}'.format(k7_mgtavcc) + '\tV\t'+'{0:.3f}'.format(z[14] / 0.01) + '\tA\t'+'{0:.3f}'.format(z[15] / 0.01) + '\tW'
                if ( (k7_mgtavcc > 1.03) or (k7_mgtavcc < 0.97) ):
                        s = '!!!!! ' + s
                print(s)

                s = 'K7_MGTAVCCAUX:\t\t' + '{0:.3f}'.format(k7_mgtavccaux) + '\tV'
                if ( (k7_mgtavccaux > (1.8 * 1.03)) or (k7_mgtavccaux < (1.8 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                s = '+2.5V_K7_A\t\t' + '{0:.3f}'.format(k7_a_2p5v) + '\tV'
                if ( (k7_a_2p5v > (2.5 * 1.03)) or (k7_a_2p5v < (2.5 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                s = '+2.5V_K7_B\t\t' + '{0:.3f}'.format(k7_b_2p5v) + '\tV'
                if ( (k7_b_2p5v > (2.5 * 1.03)) or (k7_b_2p5v < (2.5 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                s = '+3.3V_MAIN:\t\t'+'{0:.3f}'.format(main_3p3v)+'\tV\t'+'{0:.3f}'.format(z[0] / 0.004)+'\tA\t'+'{0:.3f}'.format(z[1] / 0.004)+'\tW'
                if ( (main_3p3v > (3.3 * 1.03)) or (main_3p3v < (3.3 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                print('')

                print('+12V_FMC:\t\t'+'{0:.3f}'.format(11.0 * x[2])+'\tV\t'+'{0:.3f}'.format(z[4] / 0.01)+'\tA\t'+'{0:.3f}'.format(z[5] / 0.01)+'\tW')
                print('+3.3V_FMC:\t\t'+'{0:.3f}'.format(2.0 * x[1])+'\tV\t'+'{0:.3f}'.format(z[2] / 0.004)+'\tA\t'+'{0:.3f}'.format(z[3] / 0.004)+'\tW')

		s = 'VADJ_FMC_TOP:\t\t' + '{0:.3f}'.format(vadj_fmc_top) + '\tV'
                if ( (vadj_fmc_top > (2.5 * 1.03)) or (vadj_fmc_top < (2.5 * 0.97)) ):
                        s = '!!!!! ' + s
                print(s)

                s = 'VADJ_FMC_BOT:\t\t' + '{0:.3f}'.format(vadj_fmc_bot) + '\tV'
                if ( (vadj_fmc_bot > (1.8 * 1.03)) or (vadj_fmc_bot < (1.8 * 0.97)) ):
                        s = '!!!!! ' + s
                print (s)
                
                print('VADJ SUPPLY:\t\t'+'{0:.3f}'.format(z[6] / 0.01)+'\tA\t'+'{0:.3f}'.format(z[7] / 0.01)+'\tW')

                print('')
                print('LTM4628 temperature:\t'+'{0:.2f}'.format(150.0 - ((x[4] - 0.2) / 0.0023))+'\tC')
                print('Board temperature:\t'+'{0:.2f}'.format(float(self.get_read_value('BOARD_TEMPERATURE') >> 4) * 0.0625)+'\tC')
                print('Kintex-7 temperature:\t'+'{0:.2f}'.format(float(self.get_read_value('KINTEX_TEMPERATURE') >> 4) * 0.0625)+'\tC')
                print('')
                print('Fan tach:\t\t'+str(self.get_read_value('FAN_SPEED')*60)+'\tPPM')
                print('Fan PWM duty cycle:\t'+'{0:.2f}'.format(self.get_read_value('FAN_PWM_CURRENT_DUTY_CYCLE')/2.55)+'\t%')

                print('')
                print('Spartan-6 QSFP present:\t\t'+str(self.get_read_value('SPARTAN_QSFP_PRESENT')))
                if ( self.get_read_value('SPARTAN_QSFP_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.get_read_value('SPARTAN_QSFP_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.get_read_value('SPARTAN_QSFP_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.get_read_value('SPARTAN_QSFP_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.get_read_value('SPARTAN_QSFP_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.get_read_value('SPARTAN_QSFP_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.get_read_value('SPARTAN_QSFP_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.get_read_value('SPARTAN_QSFP_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.get_read_value('SPARTAN_QSFP_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.get_read_value('SPARTAN_QSFP_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.get_read_value('SPARTAN_QSFP_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.get_read_value('SPARTAN_QSFP_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.get_read_value('SPARTAN_QSFP_RX4_POWER')) * 0.0001)+'mW')

                print('')
                print('Kintex-7 QSFP 1 present:\t'+str(self.get_read_value('KINTEX_QSFP_1_PRESENT')))
                if ( self.get_read_value('KINTEX_QSFP_1_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.get_read_value('KINTEX_QSFP_1_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.get_read_value('KINTEX_QSFP_1_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_1_RX4_POWER')) * 0.0001)+'mW')

                print('')
                print('Kintex-7 QSFP 2 present:\t'+str(self.get_read_value('KINTEX_QSFP_2_PRESENT')))
                if ( self.get_read_value('KINTEX_QSFP_2_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.get_read_value('KINTEX_QSFP_2_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.get_read_value('KINTEX_QSFP_2_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.get_read_value('KINTEX_QSFP_2_RX4_POWER')) * 0.0001)+'mW')

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
