library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library unisim;
use unisim.vcomponents.IBUFGDS;
use unisim.vcomponents.BUFG;

entity top is
  port(

    -- External 50MHz system clock
    sys_clk_p, sys_clk_n : in std_logic;

    -- LEDs
    leds : out std_logic_vector(1 downto 0);

    -- Communications
    kintex_done                          : out std_logic := '1';
    kintex_data_out_p, kintex_data_out_n : out std_logic;
    kintex_data_in_p, kintex_data_in_n   : in  std_logic

    );
end entity top;

architecture behave of top is

  -- Internal signals
  signal int_status_leds                                               : std_logic_vector(1 downto 0) := "00";
  signal pll_reset, async_reset                                        : std_logic                    := '1';
  signal clk_pll, int_clk_50mhz, int_clk_200mhz, clk_50mhz, clk_200mhz : std_logic; 
  signal pll_locked, comms_pulse, transmitting, receiving              : std_logic;
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

  -- Master reset
  master_reset : process(clk_pll)
    variable reset_counter : integer range 2000 downto 0 := 2000;
  begin
    if (rising_edge(clk_pll)) then
      if (reset_counter = 0) then
        pll_reset <= '0';
      else
        reset_counter := reset_counter - 1;
      end if;
    end if;
  end process master_reset;

  inst_input_clk : IBUFGDS
    generic map (
      DIFF_TERM  => true,
      IOSTANDARD => "LVDS_25"
      )
    port map (
      I  => sys_clk_p,
      IB => sys_clk_n,
      O  => clk_pll
      );

  -- System PLL
  inst_pll : entity work.pll
    generic map (
      DEVICE       => "KINTEX 7",
      clkin_period => 20.0,             -- 50 MHz
      gmult        => 20,               -- 1000MHz
      c0div        => 20,               -- 50MHz
      c1div        => 5                 -- 200MHz
      --c2div        => 10,               -- 100MHz
      --c3div        => 2                 -- 500MHz
      )
    port map (
      rst    => pll_reset,
      locked => pll_locked,
      clkin  => clk_pll,
      clk0   => int_clk_50mhz,
      clk1   => int_clk_200mhz
      --clk2   => int_clk_100mhz,
      --clk3   => int_clk_500mhz
      );

  inst_50mhz_bufg : BUFG
    port map (
      I => int_clk_50mhz,
      O => clk_50mhz
      );

  inst_200mhz_bufg : BUFG
    port map (
      I => int_clk_200mhz,
      O => clk_200mhz
      );

  --inst_100mhz_bufg : BUFG
  --  port map (
  --    I => int_clk_100mhz,
  --    O => clk_100mhz
  --    );

  --inst_500mhz_bufg : BUFG
  --  port map (
  --    I => int_clk_500mhz,
  --    O => clk_500mhz
  --    );

  async_reset <= not(pll_locked);

  inst_data_strobe : entity work.pulse_lengthen
    generic map (
      PULSE_LENGTH => 10000000
      )
    port map (
      clk         => clk_50mhz,
      pulse_short => comms_pulse,
      pulse_long  => int_status_leds(1)
      );

  comms_pulse <= (transmitting or receiving);

  -- 50MHz system clock
  inst_flasher : entity work.flasher
    generic map (
      HALF_PERIOD => 500,
      INPUT_CLOCK => 50000000
      )
    port map (
      async_reset => async_reset,
      clk         => clk_50mhz,
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
      async_reset   => async_reset,
      clk           => clk_50mhz,
      clk_4x        => clk_200mhz,
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
	
end architecture behave;

