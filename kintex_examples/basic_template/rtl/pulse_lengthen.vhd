library ieee;
use ieee.std_logic_1164.all;

entity pulse_lengthen is
  generic(
    PULSE_LENGTH : integer   := 10000000
    );
  port(
    clk         : in  std_logic;
    pulse_short : in  std_logic;
    pulse_long  : out std_logic
    );
end pulse_lengthen;

architecture behave of pulse_lengthen is
  signal pulse_cnt : integer range 0 to PULSE_LENGTH;
begin

  lengthen : process(clk)
  begin
    if ( rising_edge(clk) ) then

      pulse_long <= '0';
      
      if ( pulse_cnt /= 0 ) then
        pulse_cnt  <= pulse_cnt - 1;
        pulse_long <= '1';
      end if;

      if ( pulse_short = '1' ) then
        pulse_cnt  <= PULSE_LENGTH;
        pulse_long <= '1';
      end if;
      
    end if;
  end process lengthen;

end behave;

