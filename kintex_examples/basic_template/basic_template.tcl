
set outputDir .

# Top level
read_vhdl -library work rtl/top.vhd

# QF2 core
read_vhdl -library qf2_pre ../qf2_core.vhd

# Other modules
read_vhdl -library work rtl/async_to_sync_reset_shift.vhd
read_vhdl -library work rtl/flasher.vhd
read_vhdl -library work rtl/pulse_lengthen.vhd
read_vhdl -library work rtl/comms_register_map_masked.vhd
read_vhdl -library work rtl/configuration_wrapper.vhd

# Set the part and target language
set_property PART xc7k160tffg676-2 [current_project]
set_property TARGET_LANGUAGE VHDL [current_project]

#auto_detect_xpm
synth_design -top top -part xc7k160tffg676-2 -verbose

# Write post-synthesis checkpoint
#write_checkpoint -force ./post_synth.dcp

# Read constraints
read_xdc top.xdc

# Optimize netlist
opt_design

# Write-post-optimization checkpoint
#write_checkpoint -force ./post_opt.dcp

# Pull in the previous placed and routed build as a reference
#read_checkpoint -incremental ./post_route.dcp

# Place the design
place_design

# Run physical optimization if there are timing issues after placement
#if {[get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]] < 0} {
#  puts "Running physical optimization to resolve timing violations"
#  phys_opt_design
#}

# Write the post-placement checkpoint
#write_checkpoint -force ./post_place.dcp

# Route the design
route_design

# Write the post-route checkpoint
#write_checkpoint -force -incremental_synth ./post_route.dcp

# Write a timing simulation model out in Verilog (VHDL is not supported)
#write_verilog -force ./implementation_netlist.v -mode timesim -sdf_anno true

# Set bitstream options
#set_property BITSTREAM.GENERAL.COMPRESS True [current_design]
#set_property BITSTREAM.CONFIG.USERID "DEADC0DE" [current_design]
#set_property BITSTREAM.CONFIG.USR_ACCESS TIMESTAMP [current_design]
#set_property BITSTREAM.READBACK.ACTIVERECONFIG Yes [current_design]

# Write the bitstream
write_bitstream -force ./top.bit

# Output reports
#report_clocks -file clocks.rpt
#report_high_fanout_nets -file high_fanout_nets.rpt
#report_utilization -hierarchical -file utilization.rpt
#report_clock_utilization -file utilization.rpt -append
#report_datasheet -file datasheet.rpt
#report_timing_summary -file timing_summary.rpt
#report_power -file power.rpt
#report_incremental_reuse -file reuse.rpt
