--
-- Configuration wrapper
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity configuration_wrapper is
  generic (
    NUM_READ_BYTES  : integer;
    NUM_WRITE_BYTES : integer
    );
  port (
    async_reset, clk, clk_4x : in  std_logic;
    transmitting, receiving                   : out std_logic;
    led_lpc_r, led_lpc_g, led_lpc_b           : in  std_logic;
    led_hpc_r, led_hpc_g, led_hpc_b           : in  std_logic;
    data_in_p, data_in_n                      : in  std_logic;
    data_out_p, data_out_n                    : out std_logic;
    hs_data_out_p, hs_data_out_n              : out std_logic;
    INIT_READ_MAP                             : in  std_logic_vector(NUM_READ_BYTES*8-1 downto 0);
    read_map                                  : out std_logic_vector(NUM_READ_BYTES*8-1 downto 0);
    write_map                                 : in  std_logic_vector(NUM_WRITE_BYTES*8-1 downto 0);
    configuration_active                      : out std_logic
    );
end entity configuration_wrapper;

architecture behave of configuration_wrapper is

  signal sync_reset : std_logic := '1';

  ---------------------------
  -- FIFO signals
  ---------------------------
  signal inbound_available, inbound_frame_end, inbound_read     : std_logic;
  signal outbound_available, outbound_frame_end, outbound_write : std_logic;
  signal inbound_data, outbound_data                            : std_logic_vector(7 downto 0);

begin

  inst_sync_reset_gen : entity work.async_to_sync_reset_shift
    generic map (
      LENGTH => 4
      )
    port map (
      clk    => clk,
      input  => async_reset,
      output => sync_reset
      );

  -- Register map
  inst_register_map : entity work.comms_register_map_masked
    generic map (
      READ_BYTES  => NUM_READ_BYTES,
      WRITE_BYTES => NUM_WRITE_BYTES
      )
    port map (
      sync_reset         => sync_reset,
      clk                => clk,
      inbound_read       => inbound_read,
      inbound_data       => inbound_data,
      inbound_frame_end  => inbound_frame_end,
      inbound_available  => inbound_available,
      outbound_write     => outbound_write,
      outbound_data      => outbound_data,
      outbound_frame_end => outbound_frame_end,
      outbound_available => outbound_available,
      INIT_READ_MAP      => INIT_READ_MAP,
      read_map           => read_map,
      write_map          => write_map
      );

  -- QF2 core instance
  inst_qf2_core : entity work.qf2_core
    generic map (
      CHANNEL_1_ENABLE   => true,
      CHANNEL_2_ENABLE   => true,
      CHANNEL_3_ENABLE   => true,
      CHANNEL_4_ENABLE   => true,
      CHANNEL_1_LOOPBACK => false,
      CHANNEL_2_LOOPBACK => true,
      CHANNEL_3_LOOPBACK => true,
      CHANNEL_4_LOOPBACK => true
      )
    port map (
      async_reset                  => async_reset,
      clk                          => clk,
      clk_4x                       => clk_4x,
      led_lpc_r                    => led_lpc_r,
      led_lpc_g                    => led_lpc_g,
      led_lpc_b                    => led_lpc_b,
      led_hpc_r                    => led_hpc_r,
      led_hpc_g                    => led_hpc_g,
      led_hpc_b                    => led_hpc_b,
      transmitting                 => transmitting,
      receiving                    => receiving,
      data_in_p                    => data_in_p,
      data_in_n                    => data_in_n,
      data_out_p                   => data_out_p,
      data_out_n                   => data_out_n,
      channel_1_inbound_data       => inbound_data,
      channel_1_inbound_read       => inbound_read,
      channel_1_inbound_frame_end  => inbound_frame_end,
      channel_1_inbound_available  => inbound_available,
      channel_1_outbound_data      => outbound_data,
      channel_1_outbound_write     => outbound_write,
      channel_1_outbound_frame_end => outbound_frame_end,
      channel_1_outbound_available => outbound_available
      );

  configuration_active <= outbound_frame_end or inbound_frame_end;

end architecture behave;

