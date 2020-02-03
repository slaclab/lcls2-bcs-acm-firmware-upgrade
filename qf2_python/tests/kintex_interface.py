#!/bin/env python

import socket, string, time, sys

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
                self.WRITE_LENGTH = 111
                self.READ_LENGTH = 85

                # Interface socket
                self.UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
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
                
                while True:
                        try:
                                self.UDPSock.sendto(rbytes,(self.host, self.port))
                                read_bytes = self.UDPSock.recv(self.READ_LENGTH)
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

        def printFlashPage(self, page):
                # 110:108 == flash address
                # 107 == "000000" & flash_read & flash_request
                # 106 == "000000" & monitoring_read & monitoring request
                # 47 == 0000000 & flash_frame_end & flash_available
                # 46 == 0000000 & flash_data
                # 45 == 0000000 & monitoring_frame_end & monitoring_available
                # 44 == 0000000 & monitoring_data

                # Set the page address
                self.set_byte(110, (page >> 16) & 0xFF, 0xFF)
                self.set_byte(109, (page >> 8) & 0xFF, 0xFF)
                self.set_byte(108, page & 0xFF, 0xFF)
                
                # Trigger flash read
                self.set_byte(107, 0, 1)
                self.set_byte(107, 1, 1)

                # Wait to make sure it is ready
                time.sleep(.1)

                # Read while data available
                i = 0
                while self.get_byte(47) & 1:
                        print(str(i) + '\t' + hex(self.get_byte(46)) + '\t' + str(self.get_byte(47)))
                        self.set_byte(107, 0, 2)
                        self.set_byte(107, 2, 2)
                        i = i + 1

                # Trigger page read
                #self.set_byte(107, 0, 1)
                #self.set_byte(107, 1, 1)

                # Wait to make sure it is ready
                #time.sleep(1)
                
                # Read while data available
                #while self.get_byte(47) & 1:
                #        print(hex(self.get_byte(46)) + '\t' + str(self.get_byte(47)))
                #        self.set_byte(107, 0, 2)
                #        self.set_byte(107, 2, 2)
                        
                #print(self.get_byte(47))
                #print(self.get_byte(46))

        def printMonitoringData(self):
                self.__print_monitors()
                
                # 110:108 == flash address
                # 107 == "000000" & flash_read & flash_request
                # 106 == "000000" & monitoring_read & monitoring request
                # 47 == 0000000 & flash_frame_end & flash_available
                # 46 == 0000000 & flash_data
                # 45 == 0000000 & monitoring_frame_end & monitoring_available
                # 44 == 0000000 & monitoring_data

                # Trigger monitoring read
                #self.set_byte(106, 0, 1)
                #self.set_byte(106, 1, 1)

                # Wait to make sure it is ready
                #time.sleep(1)

                # Read while data available
                #i = 0
                #while self.get_byte(45) & 1:
                #        print(str(i) + '\t' + hex(self.get_byte(44)) + '\t' + str(self.get_byte(45)))
#                        self.set_byte(106, 0, 2)
 #                       self.set_byte(106, 2, 2)
  #                      i = i + 1
                
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

                if ((self.get_byte(50) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        raise Exception('Failed DRP quad write')

        def gt_drp_quad_read(self, quad, address):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(74, 1 | 0 | 4 | 0 | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable
                self.set_byte(74, 0, 1)

                if ((self.get_byte(50) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        raise Exception('Failed DRP quad write')

                return self.get_gt_drp_data_out()

        def gt_drp_channel_write(self, quad, channel, address, value):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(72, value & 0xFF, 0xFF)
                self.set_byte(73, (value >> 8) & 0xFF, 0xFF)
                self.set_byte(74, 1 | 2 | 0 | ((channel & 0x3) << 3) | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable, write
                self.set_byte(74, 0, 3)

                if ((self.get_byte(50) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        raise Exception('Failed DRP quad write')

        def gt_drp_channel_read(self, quad, channel, address):
                self.set_byte(70, address & 0xFF, 0xFF)
                self.set_byte(71, (address >> 8) & 0x1, 0x01)
                self.set_byte(74, 1 | 0 | 0 | ((channel & 0x3) << 3) | ((quad & 0x1) << 5), 0x3F) # enable | write | channel/quad | channel | quad
                # Clear enable, write
                self.set_byte(74, 0, 1)

                if ((self.get_byte(50) & 0x1) != 1): # or (res[1] != x[3]) or (res[0] != x[2]):
                        raise Exception('Failed DRP quad write')

                return self.get_gt_drp_data_out()

        def gt_eye_scan_stop(self):
                self.set_byte(74, 0x40, 0x40)

        def gt_eye_scan_start(self):
                self.set_byte(74, 0, 0x40)

        def set_gt_eye_scan_max_prescale(self, value):
                if value > 31:
                        raise Exception('Eye scan maximum prescale \"' + str(value) + '\" is too large')

                self.set_byte(79, value, 0xF)

        def set_gt_eye_scan_horizontal_range(self, value):                
                if value > 512:
                        raise Exception('Eye scan horizontal range \"' + str(value) + '\" is too large')

                self.set_byte(80, value, 0xFF)
                self.set_byte(81, (value >> 8), 0xFF)

        def get_eye_scan_done(self):
                return int((self.get_byte(83) >> 7))

        def get_eye_scan_fifo_empty(self):
                return int((self.get_byte(83) >> 6) & 0x1)

        def get_gt_drp_data_ready(self):
                return self.get_byte(50)

        def get_gt_drp_data_out(self):
                x = self.get_bytes()
                return (int(x[49]) << 8) | int(x[48])

        def gt_status(self):
                print('QPLLs REFCLOCKLOST:', hex(self.get_gt_qplls_refclklost()))
                print('QPLLs LOCKED:', hex(self.get_gt_qplls_locked()))
                print('CPLLs REFCLOCKLOST:', hex(self.get_gt_cplls_refclklost()))
                print('CPLLs LOCKED:', hex(self.get_gt_cplls_locked()))
                print('TX RESET DONE:', hex(self.get_gt_tx_reset_done()))
                print('TX FSM RESET DONE:', hex(self.get_gt_tx_fsm_reset_done()))
                print('RX RESET DONE:', hex(self.get_gt_rx_reset_done()))
                print('RX FSM RESET DONE:', hex(self.get_gt_rx_fsm_reset_done()))
                print('RX RECCLK STABLE:', hex(self.get_gt_rx_recclk_stable()))
                print('RX BYTE IS ALIGNED:', hex(self.get_gt_rx_byte_is_aligned()))
                print('RX DATA CHECKER TRACKING:', hex(self.get_gt_rx_data_checker_tracking()))
                print('RX STABILITY COUNTS:', self.get_gt_rx_stability_counts())
                print('RX DATA ERROR COUNTS:', self.get_gt_rx_data_error_counts())

        def get_eye_scan_data(self):
                if ( self.get_eye_scan_fifo_empty() ):
                        return None

                self.set_byte(77, 1, 1)
                self.set_byte(77, 0, 1)
                x = self.get_bytes()

                return [
                        int(x[82]), # prescale
                        int(x[81]) * 256 + int(x[80]), # sample
                        int(x[79]) * 256 + int(x[78])  # error
                        ]

        def get_gt_qplls_refclklost(self):
                return self.get_byte(77)
                
        def get_gt_qplls_locked(self):
                return self.get_byte(76)

        def get_gt_cplls_refclklost(self):
                return self.get_byte(75)
                
        def get_gt_cplls_locked(self):
                return self.get_byte(74)

        def get_gt_tx_reset_done(self):
                return self.get_byte(73)

        def get_gt_tx_fsm_reset_done(self):
                return self.get_byte(72)

        def get_gt_rx_reset_done(self):
                return self.get_byte(71)

        def get_gt_rx_fsm_reset_done(self):
                return self.get_byte(70)
                
        def get_gt_rx_recclk_stable(self):
                return self.get_byte(69)

        def get_gt_rx_byte_is_aligned(self):
                return self.get_byte(68)

        def get_gt_rx_data_checker_tracking(self):
                return self.get_byte(67)

        def get_gt_rx_stability_counts(self):
                x = self.get_bytes()
                return [
                        x[66],
                        x[65],
                        x[64],
                        x[63],
                        x[62],
                        x[61],
                        x[60],
                        x[59]
                        ]

        def get_gt_rx_data_error_counts(self):
                x = self.get_bytes()
                return [
                        x[58],
                        x[57],
                        x[56],
                        x[55],
                        x[54],
                        x[53],
                        x[52],
                        x[51]
                        ]

        __monitoring_cfg = {
                
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
                
        def __get_monitoring_value(self, key):
                return self.__monitoring_cfg[key][2]

        def __import_monitoring_data(self):

                # Trigger monitoring read
                self.set_byte(106, 0, 1)
                self.set_byte(106, 1, 1)

                # Wait to make sure it is ready
                time.sleep(0.1)

                # Read while data available
                i = 0
                x = bytearray()
                while self.get_byte(45) & 1:
                        #print(str(i) + '\t' + hex(self.get_byte(44)) + '\t' + str(self.get_byte(45)))
                        x.append(self.get_byte(44))
                        self.set_byte(106, 0, 2)
                        self.set_byte(106, 2, 2)
                        i = i + 1

                x.reverse()
                
                for key, value in self.__monitoring_cfg.items():
                        self.__import_monitoring_value(key, self.__monitoring_cfg, x)
                    
        def __import_monitoring_value(self, key, target, data):
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

        def __print_monitors(self):

                # TODO: Fix two's complement calculations
                # TODO: Check sense resistor values
                # TODO: Tach reading issue

                # Get the monitoring data
                self.__import_monitoring_data()

                # TODO: Provide monitoring active bit?
                #if ( self.get_write_value('MONITORING_ENABLE') == 0 ):
                #        raise Exception('Monitoring is currently disabled - data unavailable (must set MONITORING_ENABLE=1).')
                        
                #headphone_jack_sense = self.get_read_value('__JACK_SENSE')
                #is_qf2_pre = ((int(data[118] >> 1) & 1) ^ 1)
                #fan_tach = int(data[118] >> 2) & 1
                #power_state = int(data[118] >> 3) & 1
                #i2c_error_latch = int(data[115] >> 7) & 1
                #i2c_done_latch = int(data[115] >> 6) & 1
                #board_ot_shutdown_latch = int(data[115] >> 5) & 1
                #kintex_ot_shutdown_latch = int(data[115] >> 4) & 1

                print
                #print('Is QF2-pre:\t\t\t'+str(self.__get_monitoring_value('__N_IS_QF2_PRE') ^ 1))
                #print('Headphone jack present:\t\t'+str(self.__get_monitoring_value('__JACK_SENSE')))
                #print('Fan tach:\t\t\t'+str(self.__get_monitoring_value('__FAN_TACH')))
                #print('Main power state:\t\t'+str(self.__get_monitoring_value('MAIN_POWER_STATE')))
                #print('I2C done latch:\t\t\t'+str(self.__get_monitoring_value('I2C_DONE_LATCH')))
                #print('I2C error latch:\t\t'+str(self.__get_monitoring_value('I2C_ERROR_LATCH')))
                #print('Board OT shutdown latch:\t'+str(self.__get_monitoring_value('BOARD_OT_SHUTDOWN_LATCH')))
                #print('Kintex OT shutdown latch:\t'+str(self.__get_monitoring_value('KINTEX_OT_SHUTDOWN_LATCH')))

                z = []
                y = []
                x = []

                if ( self.__get_monitoring_value('INA226_0_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_0_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_0_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_1_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_1_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_1_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_2_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_2_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_2_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_3_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_3_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_3_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_4_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_4_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_4_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_5_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_5_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_5_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_6_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_6_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_6_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_7_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_7_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_7_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_8_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_8_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_8_1') * 0.00125 * z[-1])

                if ( self.__get_monitoring_value('INA226_9_0') & 0x8000 != 0 ):
                        z.append(0.0)
                        z.append(0.0)
                else:
                        z.append(self.__get_monitoring_value('INA226_9_0') * 0.0000025)
                        z.append(self.__get_monitoring_value('INA226_9_1') * 0.00125 * z[-1])

                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_0')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_1')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_2')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_3')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_4')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_5')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_6')) / 65536.0))
                x.append(float(2.56 * float(self.__get_monitoring_value('VMON_0_7')) / 65536.0))

                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_0')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_1')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_2')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_3')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_4')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_5')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_6')) / 65536.0))
                y.append(float(2.56 * float(self.__get_monitoring_value('VMON_1_7')) / 65536.0))

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
                print('LTM4628 temperature:\t'+'{0:.2f}'.format(25.0 - ((x[4] - 0.5) / 0.0023))+'\tC')
                print('Board temperature:\t'+'{0:.2f}'.format(float(self.__get_monitoring_value('BOARD_TEMPERATURE') >> 4) * 0.0625)+'\tC')
                print('Kintex-7 temperature:\t'+'{0:.2f}'.format(float(self.__get_monitoring_value('KINTEX_TEMPERATURE') >> 4) * 0.0625)+'\tC')
                print('')
                print('Fan tach:\t\t'+str(self.__get_monitoring_value('FAN_SPEED')*60)+'\tPPM')
                #print('Fan PWM duty cycle:\t'+'{0:.2f}'.format(self.__get_monitoring_value('FAN_PWM_CURRENT_DUTY_CYCLE')/2.55)+'\t%')

                print('')
                print('Spartan-6 QSFP present:\t\t'+str(self.__get_monitoring_value('SPARTAN_QSFP_PRESENT')))
                if ( self.__get_monitoring_value('SPARTAN_QSFP_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.__get_monitoring_value('SPARTAN_QSFP_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.__get_monitoring_value('SPARTAN_QSFP_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.__get_monitoring_value('SPARTAN_QSFP_RX4_POWER')) * 0.0001)+'mW')

                print('')
                print('Kintex-7 QSFP 1 present:\t'+str(self.__get_monitoring_value('KINTEX_QSFP_1_PRESENT')))
                if ( self.__get_monitoring_value('KINTEX_QSFP_1_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.__get_monitoring_value('KINTEX_QSFP_1_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.__get_monitoring_value('KINTEX_QSFP_1_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_1_RX4_POWER')) * 0.0001)+'mW')

                print('')
                print('Kintex-7 QSFP 2 present:\t'+str(self.__get_monitoring_value('KINTEX_QSFP_2_PRESENT')))
                if ( self.__get_monitoring_value('KINTEX_QSFP_2_PRESENT') == 1 ):
                        print('\tLOS:\t\t'+str(hex(self.__get_monitoring_value('KINTEX_QSFP_2_LOS'))))
                        print('\tTX FAULT:\t'+str(hex(self.__get_monitoring_value('KINTEX_QSFP_2_TX_FAULT'))))                        
                        print('\tVoltage:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_VOLTAGE')) * 0.0001)+'V')
                        print('\tTemperature:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_TEMPERATURE')) * 0.00390625)+'C')
                        print('\tTX1 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_TX1_BIAS')) * 0.001)+'mA')
                        print('\tTX2 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_TX2_BIAS')) * 0.001)+'mA')
                        print('\tTX3 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_TX3_BIAS')) * 0.001)+'mA')
                        print('\tTX4 bias:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_TX4_BIAS')) * 0.001)+'mA')
                        print('\tRX1 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_RX1_POWER')) * 0.0001)+'mW')
                        print('\tRX2 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_RX2_POWER')) * 0.0001)+'mW')
                        print('\tRX3 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_RX3_POWER')) * 0.0001)+'mW')
                        print('\tRX4 power:\t'+str(float(self.__get_monitoring_value('KINTEX_QSFP_2_RX4_POWER')) * 0.0001)+'mW')
                
