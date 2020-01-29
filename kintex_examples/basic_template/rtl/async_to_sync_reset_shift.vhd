library ieee;
use ieee.std_logic_1164.all;

entity async_to_sync_reset_shift is
  generic(
    LENGTH : integer;
    INPUT_POLARITY : std_logic := '1';
    OUTPUT_POLARITY : std_logic := '1'
    );
  port(
    clk    : in  std_logic;
    input  : in  std_logic;
    output : out std_logic
    );
end async_to_sync_reset_shift;

architecture behave of async_to_sync_reset_shift is
  signal shift : std_logic_vector(LENGTH-1 downto 0);
begin

  reset : process(input, clk)
  begin
    if ( input = INPUT_POLARITY ) then
      shift <= (others => OUTPUT_POLARITY);
    elsif ( rising_edge(clk) ) then
      shift <= shift(LENGTH-2 downto 0) & not(OUTPUT_POLARITY);
    end if;
  end process reset;

  -- Output the result on edge - helps to meet timing
  output <= shift(LENGTH-1) when rising_edge(clk);

end behave;
