#!/bin/env python

import time, argparse, kintex_interface

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Unicast IP address of board')
parser.add_argument('-l', '--loopback', action="store_true", default=False, help='Near-end PMA loopback')
parser.add_argument('-f', '--freq', default='125', help='Reference frequency in MHz')
parser.add_argument('-q', '--qpll', action="store_true", default=False, help='Use QPLL')
parser.add_argument('-p', '--prbs', action="store_true", default=False, help='PRBS-7')
parser.add_argument('-r', '--rate', help='Line rate in Gb/s')
parser.add_argument('-e', '--use_rx_buffer', action="store_true", default=False, help='Use RX elastic buffer')
parser.add_argument('-d', '--duration', default='0', help='Duration of test in seconds')
args = parser.parse_args()

if not(args.rate):
    parser.error('Line rate not set')

ref_freq = str(args.freq)
use_qpll = args.qpll
rate = args.rate
use_rx_buffer = args.use_rx_buffer

# GTX / GTH
QPLL_CFG = 0x32
QPLL_REFCLK_DIV = 0x33 # 15:11, 10:0 is QPLL_CFG(26:16)
QPLL_LOCK_CFG = 0x34
QPLL_FBDIV = 0x36 # 9:0 others are monitor enables
QPLL_FBDIV_RATIO = 0x37 # 6, 5:2 is CLKOUT_CFG

CPLL_CFG = 0x5E # 12:8 refclkdiv, 7 fbdiv_45, 6:0 fbdiv

PMA_RSV_0 = 0x99
PMA_RSV_1 = 0x9A
RXCDR_CFG_0 = 0xA8
RXCDR_CFG_1 = 0xA9
RXCDR_CFG_2 = 0xAA
RXCDR_CFG_3 = 0xAB
RXCDR_CFG_4 = 0xAC
RXCDR_CFG_5 = 0xAD
RXTXOUT_DIV = 0x88 # TX = 6:4, RX = 2:0, 1 => 0, 2 => 1, 4 => 2, 8 => 3, 16 => 4
RXBUF_CFG = 0x9D # Bit 1 = enable (TRUE=1 / FALSE=0), 7 = addr_mode(FAST=1 / FULL=0)
RXTX_XCLK_SEL = 0x59 # TX = 7 (TXUSR=1 / TXOUT=0), RX = 6 (RXUSR=1 / RXREC=0)

# CPLL configurations

cpll_fbdiv = {
    '125' : {
        '6.25'  : 3, # 5
        '6.0'   : 5, # 6
        '5.0'   : 2, # 4
        '4.0'   : 2, # 4
        '3.125' : 3, # 5
        '3.0'   : 5, # 6
        '2.5'   : 2, # 4
        '2.0'   : 2, # 4
        '1.25'  : 2, # 4
        '1.0'   : 2, # 4
        },

    }
    
cpll_fbdiv_45 = {
    '125' : {
        '6.25'  : 1, # 5
        '6.0'   : 0, # 4
        '5.0'   : 1, # 5
        '4.0'   : 0, # 4
        '3.125' : 1, # 5
        '3.0'   : 0, # 4
        '2.5'   : 1, # 5
        '2.0'   : 0, # 4
        '1.25'  : 1, # 5
        '1.0'   : 0, # 4
        },

    }

cpll_refclk_div = {
    '125' : {
        '6.25'  : 16, # 1
        '6.0'   : 16, # 1
        '5.0'   : 16, # 1
        '4.0'   : 16, # 1
        '3.125' : 16, # 1
        '3.0'   : 16, # 1
        '2.5'   : 16, # 1
        '2.0'   : 16, # 1
        '1.25'  : 16, # 1
        '1.0'   : 16, # 1
        },

    }

cpll_rxout_div = {
    '125' : {
        '6.25'  : 0, # 1
        '6.0'   : 0, # 1
        '5.0'   : 0, # 1
        '4.0'   : 0, # 1
        '3.125' : 1, # 2
        '3.0'   : 1, # 2
        '2.5'   : 1, # 2
        '2.0'   : 1, # 2
        '1.25'  : 2, # 4
        '1.0'   : 2, # 4
        },

    }

cpll_txout_div = {
    '125' : {
        '6.25'  : 0, # 1
        '6.0'   : 0, # 1
        '5.0'   : 0, # 1
        '4.0'   : 0, # 1
        '3.125' : 1, # 2
        '3.0'   : 1, # 2
        '2.5'   : 1, # 2
        '2.0'   : 1, # 2
        '1.25'  : 2, # 4
        '1.0'   : 2, # 4
        },

    }

cpll_rxcdr_cfg_1 = {
    0   : 0x1040, # 1
    1   : 0x1020, # 2
    2   : 0x1010, # 4
    3   : 0x1008, # 8
    }

# QPLL configurations

qpll_cfg = {
    '156.25' : {
        '10.3125'  : 0x0680181,
        },

    '185.7' : {
        '6.19'   : 0x06801C1,
        },

    '125' : {
        '10.0'  : 0x0680181,
        '8.0'   : 0x06801C1,
        '6.25'  : 0x06801C1,
        '5.0'   : 0x0680181,
        '4.0'   : 0x06801C1,
        '3.125' : 0x06801C1,
        '2.5'   : 0x0680181,
        '2.0'   : 0x06801C1,
        '1.25'  : 0x0680181,
        '1.0'   : 0x06801C1,
        },

    '312.3' : {
        '9.9'   : 0x0680181,
        },

    }

qpll_refclk_div = {
    '156.25' : {
        '10.3125'  : 16, # 1
        },

    '185.7' : {
        '6.19'   : 1, # 3
        },

    '125' : {
        '10.0'  : 16, # 1
        '8.0'   : 16, # 1
        '6.25'  : 0,  # 2
        '5.0'   : 16, # 1
        '4.0'   : 16, # 1
        '3.125' : 0,  # 2
        '2.5'   : 16, # 1
        '2.0'   : 16, # 1
        '1.25'  : 16, # 1
        '1.0'   : 16, # 1
        },

    '312.3' : {
        '9.9'   : 16, # 1
        }

    }

qpll_lock_cfg = {
    '156.25' : {
        '10.3125'  : 0x21e8,
        },

    '185.7' : {
        '6.19' : 0x21e8,
        },

    '125' : {
        '10.0'  : 0x21e8,
        '9.9'   : 0x21e8,
        '8.0'   : 0x21e8,
        '6.25'  : 0x21e8,
        '5.0'   : 0x21e8,
        '4.0'   : 0x21e8,
        '3.125' : 0x21e8,
        '2.5'   : 0x21e8,
        '2.0'   : 0x21e8,
        '1.25'  : 0x21e8,
        '1.0'   : 0x21e8,
        },

    '312.3' : {
        '9.9'   : 0x21e8,
        }

    }

qpll_fbdiv = {
    '156.25' : {
        '10.3125'  : 0x140, # 66
        },

    '185.7' : {
        '6.19'  : 0x170, # 100
        },

    '125' : {
        '10.0'  : 0x120, # 80
        '8.0'   : 0x0E0, # 64
        '6.25'  : 0x170, # 100
        '5.0'   : 0x120, # 80
        '4.0'   : 0x0E0, # 64
        '3.125' : 0x170, # 100
        '2.5'   : 0x120, # 80
        '2.0'   : 0x0E0, # 64
        '1.25'  : 0x120, # 80
        '1.0'   : 0x0E0, # 64
        },
    
    '312.3' : {
        '9.9'   : 0x60,  # 32
        }
    
    }

qpll_fbdiv_ratio = {
    '156.25' : {
        '10.3125'  : 0x0, # 66
        },

    '185.7' : {
        '6.19'  : 0x1,
        },

    '125' : {
        '10.0'  : 0x1,
        '8.0'   : 0x1,
        '6.25'  : 0x1,
        '5.0'   : 0x1,
        '4.0'   : 0x1,
        '3.125' : 0x1,
        '2.5'   : 0x1,
        '2.0'   : 0x1,
        '1.25'  : 0x1,
        '1.0'   : 0x1,
        },

    '312.3' : {
        '9.9'   : 0x1,
        }

    }

qpll_rxout_div = {
    '156.25' : {
        '10.3125'  : 0, # 1
        },

    '185.7' : {
        '6.19'  : 0, # 1
        },    

    '125' : {
        '10.0'  : 0, # 1
        '8.0'   : 0, # 1
        '6.25'  : 0, # 1
        '5.0'   : 1, # 2
        '4.0'   : 1, # 2
        '3.125' : 1, # 2
        '2.5'   : 2, # 4
        '2.0'   : 2, # 4
        '1.25'  : 3, # 8
        '1.0'   : 3, # 8
        },

    '312.3' : {
        '9.9'   : 0, # 1
        }
    }

qpll_txout_div = {
    '156.25' : {
        '10.3125'  : 0, # 1
        },

    '185.7' : {
        '6.19'  : 0, # 1
        },    

    '125' : {
        '10.0'  : 0, # 1
        '8.0'   : 0, # 1
        '6.25'  : 0, # 1
        '5.0'   : 1, # 2
        '4.0'   : 1, # 2
        '3.125' : 1, # 2
        '2.5'   : 2, # 4
        '2.0'   : 2, # 4
        '1.25'  : 3, # 8
        '1.0'   : 3, # 8
        },

    '312.3' : {
        '9.9'   : 0, # 1
        }

    }


qpll_rxcdr_cfg_5 = {
    '156.25' : {
        '10.3125'  : 0,
        },

    '185.7' : {
        '6.19'  : 0,
        },

    '125' : {
        '10.0'  : 0,
        '8.0'   : 0,
        '6.25'  : 0,
        '5.0'   : 0,
        '4.0'   : 0,
        '3.125' : 0,
        '2.5'   : 0,
        '2.0'   : 0,
        '1.25'  : 0,
        '1.0'   : 0,
        },

    '312.3' : {
        '9.9'   : 0,
        }

    }

qpll_rxcdr_cfg_4 = {
    '156.25' : {
        '10.3125'  : 0xb,
        },

    '185.7' : {
        '6.19'  : 0x3,
        },

    '125' : {
        '10.0'  : 0xb,
        '8.0'   : 0xb,
        '6.25'  : 0x3,
        '5.0'   : 0x3,
        '4.0'   : 0x3,
        '3.125' : 0x3,
        '2.5'   : 0x3,
        '2.0'   : 0x3,
        '1.25'  : 0x3,
        '1.0'   : 0x3,
        },
    
    '312.3' : {
        '9.9'   : 0x3,
        }
    
    }

qpll_rxcdr_cfg_3 = {
    '156.25' : {
        '10.3125'  : 0x0000,
        },

    '185.7' : {
        '6.19'  : 0x0000,
        },

    '125' : {
        '10.0'  : 0x0000,
        '8.0'   : 0x0000,
        '6.25'  : 0x0000,
        '5.0'   : 0x0000,
        '4.0'   : 0x0000,
        '3.125' : 0x0000,
        '2.5'   : 0x0000,
        '2.0'   : 0x0000,
        '1.25'  : 0x0000,
        '1.0'   : 0x0000,
        },
    
    '312.3' : {
        '9.9'   : 0x0000,
        }
    
    }

qpll_rxcdr_cfg_2 = {
    '156.25' : {
        '10.3125'  : 0x23ff,
        },

    '185.7' : {
        '6.19'  : 0x23ff,
        },

    '125' : {
        '10.0'  : 0x23ff,
        '8.0'   : 0x23ff,
        '6.25'  : 0x23ff,
        '5.0'   : 0x23ff,
        '4.0'   : 0x23ff,
        '3.125' : 0x23ff,
        '2.5'   : 0x23ff,
        '2.0'   : 0x23ff,
        '1.25'  : 0x23ff,
        '1.0'   : 0x23ff,
        },
    
    '312.3' : {
        '9.9'   : 0x23ff,
        }

    }

qpll_rxcdr_cfg_1 = {
    '156.25' : {
        '10.3125'  : 0x1040,
        },

    '185.7' : {
        '6.19'  : 0x2040,
        },

    '125' : {
        '10.0'  : 0x1040,
        '8.0'   : 0x1040,
        '6.25'  : 0x2040,
        '5.0'   : 0x4020,
        '4.0'   : 0x4020,
        '3.125' : 0x4020,
        '2.5'   : 0x4008,
        '2.0'   : 0x4008,
        '1.25'  : 0x4004,
        '1.0'   : 0x4004,
        },
    
    '312.3' : {
        '9.9'   : 0x1040,
        }

    }

qpll_rxcdr_cfg_0 = {
    '156.25' : {
        '10.3125'  : 0x0020,
        },

    '185.7' : {
        '6.19'  : 0x0020,
        },

    '125' : {
        '10.0'  : 0x0020,
        '8.0'   : 0x0020,
        '6.25'  : 0x0020,
        '5.0'   : 0x0020,
        '4.0'   : 0x0020,
        '3.125' : 0x0020,
        '2.5'   : 0x0020,
        '2.0'   : 0x0020,
        '1.25'  : 0x0020,
        '1.0'   : 0x0020,
        },
    
    '312.3' : {
        '9.9'   : 0x0020,
        }

    }

# AR45360
# QPLL higher line rates (>= 6.6G) = x1E7080
# CPLL full range, QPLL < 6.6G = x18480

qpll_pma_rsv_1 = {
    '156.25' : {
        '10.3125'  : 0x001E,
        },

    '185.7' : {
        '6.19'  : 0x0001,
        },

    '125' : {
        '10.0'  : 0x001E,
        '8.0'   : 0x001E,
        '6.25'  : 0x0001,
        '5.0'   : 0x001E,
        '4.0'   : 0x001E,
        '3.125' : 0x0001,
        '2.5'   : 0x001E,
        '2.0'   : 0x001E,
        '1.25'  : 0x001E,
        '1.0'   : 0x001E,
        },

    '312.3' : {
        '9.9'   : 0x001E,
        }
    
    }

qpll_pma_rsv_0 = {
    '156.25' : {
        '10.3125'  : 0x7080,
        },

    '185.7' : {
        '6.19'  : 0x8480,
        },

    '125' : {
        '10.0'  : 0x7080,
        '8.0'   : 0x7080,
        '6.25'  : 0x8480,
        '5.0'   : 0x7080,
        '4.0'   : 0x7080,
        '3.125' : 0x8480,
        '2.5'   : 0x7080,
        '2.0'   : 0x7080,
        '1.25'  : 0x7080,
        '1.0'   : 0x7080,
    },

    '312.3' : {
        '9.9'   : 0x7080,
        }

    }

if use_qpll:
    new_qpll_cfg = qpll_cfg[ref_freq][rate]
    new_qpll_refclk_div = qpll_refclk_div[ref_freq][rate]
    new_qpll_lock_cfg = qpll_lock_cfg[ref_freq][rate]
    new_qpll_fbdiv = qpll_fbdiv[ref_freq][rate]
    new_qpll_fbdiv_ratio = qpll_fbdiv_ratio[ref_freq][rate]

    new_rxcdr_cfg_0 = qpll_rxcdr_cfg_0[ref_freq][rate]
    new_rxcdr_cfg_1 = qpll_rxcdr_cfg_1[ref_freq][rate]
    new_rxcdr_cfg_2 = qpll_rxcdr_cfg_2[ref_freq][rate]
    new_rxcdr_cfg_3 = qpll_rxcdr_cfg_3[ref_freq][rate]
    new_rxcdr_cfg_4 = qpll_rxcdr_cfg_4[ref_freq][rate]
    new_rxcdr_cfg_5 = qpll_rxcdr_cfg_5[ref_freq][rate]
    new_rxout_div = qpll_rxout_div[ref_freq][rate]
    new_txout_div = qpll_txout_div[ref_freq][rate]
    new_pma_rsv_0 = qpll_pma_rsv_0[ref_freq][rate]
    new_pma_rsv_1 = qpll_pma_rsv_1[ref_freq][rate]
else:
    new_cpll_cfg = (cpll_refclk_div[ref_freq][rate] << 8) | (cpll_fbdiv_45[ref_freq][rate] << 7) | cpll_fbdiv[ref_freq][rate]
    new_rxout_div = cpll_rxout_div[ref_freq][rate]
    new_txout_div = cpll_txout_div[ref_freq][rate]
    new_rxcdr_cfg_0 = 0x0020
    new_rxcdr_cfg_1 = cpll_rxcdr_cfg_1[new_rxout_div]
    new_rxcdr_cfg_2 = 0x23FF
    new_rxcdr_cfg_3 = 0x0000
    new_rxcdr_cfg_4 = 0x3
    new_rxcdr_cfg_5 = 0x0
    new_pma_rsv_0 = 0x8480
    new_pma_rsv_1 = 0x0001

# Get an interface
x = kintex_interface.interface(args.target)

# Turn on the transceivers
x.gt_tx_power_up()
x.gt_rx_power_up()

# Wait for powerup
time.sleep(1)

# Reconfigure the clock system
for quad in range(0, 2):

    print 'Quad',quad

    if use_qpll:
        x.gt_drp_quad_write(quad, QPLL_FBDIV_RATIO, (x.gt_drp_quad_read(quad, QPLL_FBDIV_RATIO) & 0xFFBF) | (new_qpll_fbdiv_ratio << 6))
        x.gt_drp_quad_write(quad, QPLL_FBDIV, (x.gt_drp_quad_read(quad, QPLL_FBDIV) & 0xFC00) | new_qpll_fbdiv)
        x.gt_drp_quad_write(quad, QPLL_LOCK_CFG, new_qpll_lock_cfg)
        x.gt_drp_quad_write(quad, QPLL_CFG, new_qpll_cfg & 0xFFFF)
        x.gt_drp_quad_write(quad, QPLL_REFCLK_DIV, (new_qpll_refclk_div << 11) | ((new_qpll_cfg >> 16) & 0x7FF))

        print 'QPLL_CFG:', hex(((x.gt_drp_quad_read(quad, QPLL_REFCLK_DIV) & 0x7FF) << 16) | x.gt_drp_quad_read(quad, QPLL_CFG))
        print 'QPLL_REFCLK_DIV:', hex(x.gt_drp_quad_read(quad, QPLL_REFCLK_DIV) >> 11)
        print 'QPLL_LOCK_CFG:', hex(x.gt_drp_quad_read(quad, QPLL_LOCK_CFG))
        print 'QPLL_FBDIV:', hex(x.gt_drp_quad_read(quad, QPLL_FBDIV) & 0x3FF)
        print 'QPLL_FBDIV_RATIO:', hex((x.gt_drp_quad_read(quad, QPLL_FBDIV_RATIO) >> 6) & 0x1)

        print

    for channel in range(0, 4):

        print 'Channel',channel

        # Update settings
        x.gt_drp_channel_write(quad, channel, PMA_RSV_0, new_pma_rsv_0)
        x.gt_drp_channel_write(quad, channel, PMA_RSV_1, new_pma_rsv_1)
        x.gt_drp_channel_write(quad, channel, RXTXOUT_DIV, new_txout_div << 4 | new_rxout_div)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_0, new_rxcdr_cfg_0)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_1, new_rxcdr_cfg_1)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_2, new_rxcdr_cfg_2)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_3, new_rxcdr_cfg_3)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_4, new_rxcdr_cfg_4)
        x.gt_drp_channel_write(quad, channel, RXCDR_CFG_5, new_rxcdr_cfg_5)

        if ( use_rx_buffer ):
            x.gt_drp_channel_write(quad, channel, RXTX_XCLK_SEL, 0xFFBF & x.gt_drp_channel_read(quad, channel, RXTX_XCLK_SEL))
            x.gt_drp_channel_write(quad, channel, RXBUF_CFG, 0x2 | x.gt_drp_channel_read(quad, channel, RXBUF_CFG))
        else:
            x.gt_drp_channel_write(quad, channel, RXTX_XCLK_SEL, 0x40 | x.gt_drp_channel_read(quad, channel, RXTX_XCLK_SEL))
            x.gt_drp_channel_write(quad, channel, RXBUF_CFG, 0xFFFD & x.gt_drp_channel_read(quad, channel, RXBUF_CFG))

        # Only if using QPLL
        if not(use_qpll):
            x.gt_drp_channel_write(quad, channel, CPLL_CFG, new_cpll_cfg)
            print 'CPLL_CFG:', hex(x.gt_drp_channel_read(quad, channel, CPLL_CFG))

        # Channel-specific
        print 'RXOUT_DIV:', x.gt_drp_channel_read(quad, channel, RXTXOUT_DIV) & 0x7
        print 'TXOUT_DIV:', (x.gt_drp_channel_read(quad, channel, RXTXOUT_DIV) >> 4) & 0x7
        print 'RXCDR_CFG:', hex(x.gt_drp_channel_read(quad, channel, RXCDR_CFG_5) << 80 | x.gt_drp_channel_read(quad, channel, RXCDR_CFG_4) << 64 | x.gt_drp_channel_read(quad, channel, RXCDR_CFG_3) << 48 | x.gt_drp_channel_read(quad, channel, RXCDR_CFG_2) << 32 | x.gt_drp_channel_read(quad, channel, RXCDR_CFG_1) << 16 | x.gt_drp_channel_read(quad, channel, RXCDR_CFG_0))
        print 'PMA_RSV:', hex(x.gt_drp_channel_read(quad, channel, PMA_RSV_1) << 16 | x.gt_drp_channel_read(quad, channel, PMA_RSV_0))
        print 'RXBUF_CFG:', hex(x.gt_drp_channel_read(quad, channel, RXBUF_CFG))
        print 'RXTX_XCLK_SEL:', hex(x.gt_drp_channel_read(quad, channel, RXTX_XCLK_SEL))

        print

start_time = time.time()

if args.loopback:
    x.gt_loopback(kintex_interface.GTX_LOOPBACK_MODES.NEAR_END_PMA)
else:
    x.gt_loopback(kintex_interface.GTX_LOOPBACK_MODES.NORMAL)

if args.qpll:
    x.gt_use_qpll()
else:
    x.gt_use_cpll()

if args.prbs:
    x.gt_prbs_enable()
else:
    x.gt_prbs_disable()

# Reset the transceivers and monitors
x.gt_reset()
x.gt_rx_reset()
x.gt_rx_stability_counter_reset()
x.gt_rx_data_checker_reset()
print

while True:
    print('Elapsed: '+str(int(time.time() - start_time)))
    print('')

    # Status
    x.gt_status()
    print

    if int(args.duration) != 0:
        if (int(args.duration) + start_time) < time.time():
            print('Test complete')
            break

    time.sleep(1)
