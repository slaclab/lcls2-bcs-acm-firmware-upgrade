library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.IBUFGDS;
use unisim.vcomponents.BUFG;

library work;

entity top is
  port(

    -- External 50MHz system clock
    clk_sys_p, clk_sys_n : in std_logic;
    
    -- LEDs
    leds : out std_logic_vector(1 downto 0);

    -- Communications
    kintex_data_out_p, kintex_data_out_n : out std_logic;
    kintex_data_in_p, kintex_data_in_n   : in  std_logic;
    kintex_rx_locked : out std_logic
    
    );
end entity top;

architecture rtl of top is

  -- Internal signals
  signal int_status_leds                                               : std_logic_vector(1 downto 0) := "00";
  signal async_reset                                        : std_logic                    := '1';
  signal clk_100mhz : std_logic; 
  signal comms_pulse, transmitting, receiving              : std_logic;
  signal led_0_red, led_0_green, led_0_blue                            : std_logic;
  signal led_1_red, led_1_green, led_1_blue                            : std_logic;

  -- Configuration map
  constant NUM_WRITE_BYTES : integer := 2;
  constant NUM_READ_BYTES  : integer := 2;

  signal configuration_read_map  : std_logic_vector(NUM_READ_BYTES*8-1 downto 0);
  signal configuration_write_map : std_logic_vector(NUM_WRITE_BYTES*8-1 downto 0);

  constant init_configuration_read_map : std_logic_vector(NUM_READ_BYTES*8-1 downto 0) :=

    -- LED drive signals
    "00000000" & -- [7:3] == "XXXXX", [2] == LED 1 BLUE, [1] == LED 1 GREEN, [0] == LED 1 RED
    "00000000"   -- [7:3] == "XXXXX", [2] == LED 0 BLUE, [1] == LED 0 GREEN, [0] == LED 0 RED
	 
	 ;

begin

  inst_data_strobe : entity work.pulse_lengthen
    generic map (
      PULSE_LENGTH => 10000000
      )
    port map (
      clk         => clk_100mhz,
      pulse_short => comms_pulse,
      pulse_long  => int_status_leds(1)
      );

  comms_pulse <= transmitting or receiving;

  -- 100MHz system clock
  inst_flasher : entity work.flasher
    generic map (
      HALF_PERIOD => 500,
      INPUT_CLOCK => 100000000
      )
    port map (
      async_reset => async_reset,
      clk         => clk_100mhz,
      output      => int_status_leds(0)
      );

  leds <= int_status_leds;

  -- Configuration wrapper
  inst_configuration_wrapper : entity work.configuration_wrapper
    generic map (
      NUM_READ_BYTES  => NUM_READ_BYTES,
      NUM_WRITE_BYTES => NUM_WRITE_BYTES
      )
    port map (
      clk_sys_p => clk_sys_p,
      clk_sys_n => clk_sys_n,
      async_reset   => async_reset,
      clk_100mhz    => clk_100mhz,
      led_lpc_r     => led_0_red,
      led_lpc_g     => led_0_green,
      led_lpc_b     => led_0_blue,
      led_hpc_r     => led_1_red,
      led_hpc_g     => led_1_green,
      led_hpc_b     => led_1_blue,
      transmitting  => transmitting,
      receiving     => receiving,
      data_in_p     => kintex_data_in_p,
      data_in_n     => kintex_data_in_n,
      data_out_p    => kintex_data_out_p,
      data_out_n    => kintex_data_out_n,
      rx_locked     => kintex_rx_locked,
      INIT_READ_MAP => init_configuration_read_map,
      read_map      => configuration_read_map,
      write_map     => configuration_write_map
      );

  -- Configuration write map
  configuration_write_map(configuration_write_map'left downto 0) <=
    "00000" & led_1_blue & led_1_green & led_1_red &
    "00000" & led_0_blue & led_0_green & led_0_red
    ;
  
  -- Configuration read map
  led_0_red <= configuration_read_map(0);
  led_0_green <= configuration_read_map(1);
  led_0_blue <= configuration_read_map(2);

  led_1_red <= configuration_read_map(8);
  led_1_green <= configuration_read_map(9);
  led_1_blue <= configuration_read_map(10);

end architecture rtl;

