#!/bin/env python

from socket import *
import time

class interface():

        def __init__(self, target):

                self.host = target
                self.port = 50004
                self.WRITE_LENGTH = 2
                self.READ_LENGTH = 2
                

                # Interface socket
                self.UDPSock = socket(AF_INET,SOCK_DGRAM)
                self.UDPSock.bind(("0.0.0.0", 0))
                self.UDPSock.settimeout(1)

        def set_byte(self, index, data, mask):
                d = bytearray(self.WRITE_LENGTH)
                m = bytearray(self.WRITE_LENGTH)
                d[index] = data
                m[index] = mask
                self.send_receive(d, m)

        def get_byte(self, index):
                d = bytearray(self.WRITE_LENGTH)
                m = bytearray(self.WRITE_LENGTH)
                res = self.send_receive(d, m)
                return res[index]

        def get_bytes(self):
                d = bytearray(self.WRITE_LENGTH)
                m = bytearray(self.WRITE_LENGTH)
                return self.send_receive(d, m)

        def send_receive(self, data, mask):

                data.reverse()
                mask.reverse()
                rbytes = bytearray()
                rbytes[:] = (mask + data)

                self.UDPSock.sendto(rbytes,(self.host, self.port))
                read_bytes = self.UDPSock.recv(1000)
                if not read_bytes:
                        print('No data received')
                if len(read_bytes) == 0:
                        print('No data received')

                res = bytearray(read_bytes)
                res.reverse()

                return res

        def setTopLED(self, *, red, green, blue):
                v = 0
                if red:
                        v = 1
                if green:
                        v = v | 2
                if blue:
                        v = v | 4
                self.set_byte(0, v, 0xFF)

        def setBottomLED(self, *, red, green, blue):
                v = 0
                if red:
                        v = 1
                if green:
                        v = v | 2
                if blue:
                        v = v | 4
                self.set_byte(1, v, 0xFF)
                
