#!/bin/env python

from socket import *
import string, time, sys

class GTX_LOOPBACK_MODES:
        NORMAL = 0
        NEAR_END_PCS = 1
        NEAR_END_PMA = 2
        FAR_END_PMA = 4
        FAR_END_PCS = 6

class interface():

        def __init__(self, target):

                self.host = target
                self.port = 50004
                self.WRITE_LENGTH = 106
                self.READ_LENGTH = 81

                # Interface socket
                self.UDPSock = socket(AF_INET,SOCK_DGRAM)
                self.UDPSock.bind(("0.0.0.0", 0))
                self.UDPSock.settimeout(0.05)

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
                
                read_bytes = str()

                while True:
                        try:
                                self.UDPSock.sendto(str(rbytes),(self.host, self.port))
                                read_bytes = self.UDPSock.recv(self.READ_LENGTH)
                                if not read_bytes:
                                        print "No data received"
                                break
                        except KeyboardInterrupt:
                                print 'Ctrl-C detected'
                                exit(0)
                        except:
                                continue

                res = bytearray(read_bytes)
                res.reverse()

                return res

        def print_io_status(self):

                print('TOP FMC LA P:\t\t'+'{0:034b}'.format(self.get_top_fmc_la_p()))
                print('TOP FMC LA N:\t\t'+'{0:034b}'.format(self.get_top_fmc_la_n()))
                print('BOTTOM FMC LA P:\t'+'{0:034b}'.format(self.get_bottom_fmc_la_p()))
                print('BOTTOM FMC LA N:\t'+'{0:034b}'.format(self.get_bottom_fmc_la_n()))
                print('BOTTOM FMC HA P:\t'+'{0:024b}'.format(self.get_bottom_fmc_ha_p()))
                print('BOTTOM FMC HA N:\t'+'{0:024b}'.format(self.get_bottom_fmc_ha_n()))
                print('BOTTOM FMC HB P:\t'+'{0:022b}'.format(self.get_bottom_fmc_hb_p()))
                print('BOTTOM FMC HB N:\t'+'{0:022b}'.format(self.get_bottom_fmc_hb_n()))
                print('FULL MFC P:\t\t'+'{0:024b}'.format(self.get_full_mfc_p()))
                print('FULL MFC N:\t\t'+'{0:024b}'.format(self.get_full_mfc_n()))
                print('AUX MFC P:\t\t'+'{0:020b}'.format(self.get_aux_mfc_p()))
                print('AUX MFC N:\t\t'+'{0:020b}'.format(self.get_aux_mfc_n()))

        def set_top_fmc_la_p(self, d, m):
                m = (m ^ 0x3FFFFFFFF)

                for i in range(0, 5):
                        self.set_byte(i, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 32, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_top_fmc_la_n(self, d, m):
                m = (m ^ 0x3FFFFFFFF)

                for i in range(0, 5):
                        self.set_byte(i + 5, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 32 + 5, (d >> (i * 8)) & 0xFF, 0xFF)

        def get_top_fmc_la_p(self):
                return self.get_io_bits_as_val(31, 5)

        def get_top_fmc_la_n(self):
                return self.get_io_bits_as_val(26, 5)

        def set_bottom_fmc_la_p(self, d, m):
                m = (m ^ 0x3FFFFFFFF)

                for i in range(0, 5):
                        self.set_byte(i + 10, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 42, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_bottom_fmc_la_n(self, d, m):
                m = (m ^ 0x3FFFFFFFF)

                for i in range(0, 5):
                        self.set_byte(i + 10 + 5, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 42 + 5, (d >> (i * 8)) & 0xFF, 0xFF)

        def get_bottom_fmc_la_p(self):
                return self.get_io_bits_as_val(21, 5)

        def get_bottom_fmc_la_n(self):
                return self.get_io_bits_as_val(16, 5)

        def set_bottom_fmc_ha_p(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 20, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 52, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_bottom_fmc_ha_n(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 20 + 3, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 52 + 3, (d >> (i * 8)) & 0xFF, 0xFF)

        def get_bottom_fmc_ha_p(self):
                return self.get_io_bits_as_val(11, 3)

        def get_bottom_fmc_ha_n(self):
                return self.get_io_bits_as_val(8, 3)

        def set_bottom_fmc_hb_p(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 26, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 58, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_bottom_fmc_hb_n(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 26 + 3, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 58 + 3, (d >> (i * 8)) & 0xFF, 0xFF)

        def get_bottom_fmc_hb_p(self):
                return self.get_io_bits_as_val(5, 3)

        def get_bottom_fmc_hb_n(self):
                return self.get_io_bits_as_val(2, 3)

        def set_full_mfc_p(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 82, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 88, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_full_mfc_n(self, d, m):
                m = (m ^ 0xFFFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 85, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 91, (d >> (i * 8)) & 0xFF, 0xFF)

        def get_full_mfc_p(self):
                return self.get_io_bits_as_val(37, 3)

        def get_full_mfc_n(self):
                return self.get_io_bits_as_val(34, 3)

        def get_aux_mfc_p(self):
                return self.get_io_bits_as_val(43, 3)

        def get_aux_mfc_n(self):
                return self.get_io_bits_as_val(40, 3)

        def get_io_bits_as_val(self, index, length):
                x = self.get_bytes()
                
                val = 0
                for i in range(0, length):
                        val = val | int(x[index] << ((length - 1 - i) * 8))
                        index = index - 1
                
                return val

        def set_aux_mfc_p(self, d, m):
                m = (m ^ 0x0FFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 94, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 100, (d >> (i * 8)) & 0xFF, 0xFF)

        def set_aux_mfc_n(self, d, m):
                m = (m ^ 0x0FFFFF)

                for i in range(0, 3):
                        self.set_byte(i + 97, ((m >> (i * 8)) & 0xFF), 0xFF)
                        self.set_byte(i + 103, (d >> (i * 8)) & 0xFF, 0xFF)

        def gt_clock_select(self, value):
                # Set ref_clk_sel pins for two quads
                self.set_byte(67, value, 0x3F)
                
        def gt_reset(self):
                # Pulse reset
                self.set_byte(68, 3, 3)
                time.sleep(0.1)
                self.set_byte(68, 0, 3)
                time.sleep(0.1)

        def gt_tx_reset(self):
                # Pulse reset
                self.set_byte(68, 1, 1)
                time.sleep(0.1)
                self.set_byte(68, 0, 1)
                time.sleep(0.1)

        def gt_rx_reset(self):
                # Pulse reset
                self.set_byte(68, 2, 2)
                time.sleep(0.1)
                self.set_byte(68, 0, 2)
                time.sleep(0.1)

        def gt_rx_stability_counter_reset(self):
                # Pulse reset
                self.set_byte(68, 4, 4)
                self.set_byte(68, 0, 4)

        def gt_rx_data_checker_reset(self):
                # Pulse reset
                self.set_byte(68, 8, 8)
                self.set_byte(68, 0, 8)

        def gt_prbs_enable(self):
                self.set_byte(68, 0x10, 0x10)

        def gt_prbs_disable(self):
                self.set_byte(68, 0, 0x10)

        def gt_tx_power_down(self):
                self.set_byte(68, 0x20, 0x20)

        def gt_tx_power_up(self):
                self.set_byte(68, 0, 0x20)

        def gt_rx_power_down(self):
                self.set_byte(68, 0x40, 0x40)

        def gt_rx_power_up(self):
                self.set_byte(68, 0, 0x40)

        def gt_use_qpll(self):
                self.set_byte(68, 0x80, 0x80)

        def gt_use_cpll(self):
                self.set_byte(68, 0, 0x80)

        def gt_loopback(self, value):
                self.set_byte(69, value, 7)

        def gt_drp_quad_write(self, quad, address, value):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(72, value & 0xFF, 0xFF)
                self.set_byte(73, (value >> 8) & 0xFF, 0xFF)
                self.set_byte(74, 1 | 2 | 4 | 0 | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable, write
                self.set_byte(74, 0, 3)

                if ((self.get_byte(46) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        print "Failed DRP quad write"
                        exit()

        def gt_drp_quad_read(self, quad, address):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(74, 1 | 0 | 4 | 0 | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable
                self.set_byte(74, 0, 1)

                if ((self.get_byte(46) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        print "Failed DRP quad write"
                        exit()

                return self.get_gt_drp_data_out()

        def gt_drp_channel_write(self, quad, channel, address, value):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(72, value & 0xFF, 0xFF)
                self.set_byte(73, (value >> 8) & 0xFF, 0xFF)
                self.set_byte(74, 1 | 2 | 0 | ((channel & 0x3) << 3) | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable, write
                self.set_byte(74, 0, 3)

                if ((self.get_byte(46) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        print "Failed DRP quad write"
                        exit()

        def gt_drp_channel_read(self, quad, channel, address):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(74, 1 | 0 | 0 | ((channel & 0x3) << 3) | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable, write
                self.set_byte(74, 0, 1)

                if ((self.get_byte(46) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        print "Failed DRP quad write"
                        exit()

                return self.get_gt_drp_data_out()

        def gt_eye_scan_stop(self):
                self.set_byte(74, 0x40, 0x40)

        def gt_eye_scan_start(self):
                self.set_byte(74, 0, 0x40)

        def set_gt_eye_scan_max_prescale(self, value):
                if value > 31:
                        print 'Eye scan maximum prescale', str(value), 'too large'
                        exit(1)

                self.set_byte(79, value, 0xF)

        def set_gt_eye_scan_horizontal_range(self, value):                
                if value > 512:
                        print 'Eye scan horizontal range', str(value), 'too large'
                        exit(1)

                self.set_byte(80, value, 0xFF)
                self.set_byte(81, (value >> 8), 0xFF)

        def get_eye_scan_done(self):
                return int((self.get_byte(79) >> 7))

        def get_eye_scan_fifo_empty(self):
                return int((self.get_byte(79) >> 6) & 0x1)

        def get_gt_drp_data_ready(self):
                return self.get_byte(46)

        def get_gt_drp_data_out(self):
                x = self.get_bytes()
                return (int(x[45]) << 8) | int(x[44])

        def gt_status(self):
                print 'QPLLs REFCLOCKLOST:', hex(self.get_gt_qplls_refclklost())
                print 'QPLLs LOCKED:', hex(self.get_gt_qplls_locked())
                print 'CPLLs REFCLOCKLOST:', hex(self.get_gt_cplls_refclklost())
                print 'CPLLs LOCKED:', hex(self.get_gt_cplls_locked())
                print 'TX RESET DONE:', hex(self.get_gt_tx_reset_done())
                print 'TX FSM RESET DONE:', hex(self.get_gt_tx_fsm_reset_done())
                print 'RX RESET DONE:', hex(self.get_gt_rx_reset_done())
                print 'RX FSM RESET DONE:', hex(self.get_gt_rx_fsm_reset_done())
                print 'RX RECCLK STABLE:', hex(self.get_gt_rx_recclk_stable())
                print 'RX BYTE IS ALIGNED:', hex(self.get_gt_rx_byte_is_aligned())
                print 'RX DATA CHECKER TRACKING:', hex(self.get_gt_rx_data_checker_tracking())
                print 'RX STABILITY COUNTS:', self.get_gt_rx_stability_counts()
                print 'RX DATA ERROR COUNTS:', self.get_gt_rx_data_error_counts()

        def get_eye_scan_data(self):
                if ( self.get_eye_scan_fifo_empty() ):
                        return None

                self.set_byte(77, 1, 1)
                self.set_byte(77, 0, 1)
                x = self.get_bytes()

                return [
                        int(x[78]), # prescale
                        int(x[77]) * 256 + int(x[76]), # sample
                        int(x[75]) * 256 + int(x[74])  # error
                        ]

        def get_gt_qplls_refclklost(self):
                return self.get_byte(73)
                
        def get_gt_qplls_locked(self):
                return self.get_byte(72)

        def get_gt_cplls_refclklost(self):
                return self.get_byte(71)
                
        def get_gt_cplls_locked(self):
                return self.get_byte(70)

        def get_gt_tx_reset_done(self):
                return self.get_byte(69)

        def get_gt_tx_fsm_reset_done(self):
                return self.get_byte(68)

        def get_gt_rx_reset_done(self):
                return self.get_byte(67)

        def get_gt_rx_fsm_reset_done(self):
                return self.get_byte(66)
                
        def get_gt_rx_recclk_stable(self):
                return self.get_byte(65)

        def get_gt_rx_byte_is_aligned(self):
                return self.get_byte(64)

        def get_gt_rx_data_checker_tracking(self):
                return self.get_byte(63)

        def get_gt_rx_stability_counts(self):
                x = self.get_bytes()
                return [
                        x[62],
                        x[61],
                        x[60],
                        x[59],
                        x[58],
                        x[57],
                        x[56],
                        x[55]
                        ]

        def get_gt_rx_data_error_counts(self):
                x = self.get_bytes()
                return [
                        x[54],
                        x[53],
                        x[52],
                        x[51],
                        x[50],
                        x[49],
                        x[48],
                        x[47]
                        ]
