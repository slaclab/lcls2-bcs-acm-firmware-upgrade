set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

############################################
# Clocks
#

set_property IOSTANDARD LVDS_25 [get_ports clk_sys_*]
set_property DIFF_TERM TRUE [get_ports clk_sys_*]

set_property PACKAGE_PIN G11 [get_ports clk_sys_p]
set_property PACKAGE_PIN F10 [get_ports clk_sys_n]

create_clock -name clk_sys -period 20.0 [get_ports clk_sys_p]

############################################
# LEDs
#

set_property IOSTANDARD LVCMOS25 [get_ports leds[*]]
#set_property SLEW SLOW [get_ports ttl_lemo_outputs[*]]
#set_property DRIVE 4 [get_ports ttl_lemo_outputs[*]]

set_property PACKAGE_PIN M16 [get_ports leds[0]]
set_property PACKAGE_PIN K15 [get_ports leds[1]]

############################################
# Communications
#

set_property IOSTANDARD LVDS_25 [get_ports kintex_data_*]
set_property DIFF_TERM TRUE [get_ports kintex_data_in_*]

set_property PACKAGE_PIN J11 [get_ports kintex_data_out_p]
set_property PACKAGE_PIN J10 [get_ports kintex_data_out_n]

set_property PACKAGE_PIN J13 [get_ports kintex_data_in_p]
set_property PACKAGE_PIN H13 [get_ports kintex_data_in_n]

