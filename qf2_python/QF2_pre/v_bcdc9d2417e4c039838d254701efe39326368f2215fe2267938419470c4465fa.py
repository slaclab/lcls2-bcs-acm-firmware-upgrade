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
        __read_bytes = 59

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
                
                # SYS I2C DEBUG IGNORED

                '__N_TAS_2505_RESET' : [10, 1, int(0)],
                
                'AUTOBOOT_TO_RUNTIME' : [4, 1, int(0)],
                
                '__SYS_I2C_RESET' : [2, 1, int(1)],
                '__SYS_I2C_SDA' : [1, 1, int(1)],
                '__SYS_I2C_SCL' : [0, 1, int(1)]

        }

        # Key : [Start (bits), Length (bits), Type]
        __read_cfg = {

                #TAS COUNT, CORRUPTED BITSTREAM, FLASH DEBUG

                '__FAN_TACH' : [51*8+2, 1, int()],
                '__N_IS_QF2P' : [51*8+1, 1, int()],
                '__JACK_SENSE' : [51*8, 1, int()]

        }

class interface(cfg):

        def __init__(self, host, verbose):
                # Initialize the configuration layer
                cfg.__init__(self, verbose)

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

                raise Exception('This is an intentional exception - the bootloader interface is a placeholder for future use.')

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
                                read_bytes = self.UDPSock.recv(cfg.read_length(self))
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
