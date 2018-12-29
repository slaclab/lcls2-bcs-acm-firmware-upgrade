LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_arith.all;

ENTITY flasher IS
  GENERIC(
    HALF_PERIOD : natural := 1000; -- flasher half-period in milliseconds
    INPUT_CLOCK : natural := 40000000 -- frequency of input clock to flasher (Hz)
    );
  PORT(
    async_reset : in std_logic;
    clk         : in std_logic;
    gate        : in std_logic := '1';
    output      : out std_logic
    );
END flasher;

ARCHITECTURE v0 OF flasher IS
  signal int_output : std_logic := '1';
BEGIN

  flasher : process (async_reset, clk)
    variable counter : natural := (INPUT_CLOCK / 1000) * HALF_PERIOD;
  begin

    if ( async_reset = '1' ) then
      -- hold output on in reset
      int_output <= '1';
      counter := (INPUT_CLOCK / 1000) * HALF_PERIOD;
    elsif ( rising_edge(clk) ) then
      if ( gate = '1' ) then
        if ( counter = 0 ) then
          int_output <= not(int_output);                
          counter := (INPUT_CLOCK / 1000) * HALF_PERIOD;
        else
          counter := counter - 1;
        end if;
      end if;
    end if;        

  end process flasher;

  -- transfer local register to output
  output <= int_output;

END ARCHITECTURE v0;

