--
-- Masked register map
--
-- This is a very simple implementation:
-- It is expected that a packet matches the size of the
-- configuration space. If not, the packet is thrown away
-- and no response is sent. We are also therefore limited to
-- less than ~1500 bytes as this is the MTU size for Ethernet
-- when not using jumbo frames.
--
-- The packet size must match the register space dimensions
-- because the data is basically shifted then copied across.
--
-- 

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity comms_register_map_masked is
  generic (
    READ_BYTES  : integer;
    WRITE_BYTES : integer
    );
  port (
    clk, sync_reset : in std_logic;

    -- Stream interface
    inbound_read      : out std_logic;
    inbound_data      : in  std_logic_vector(7 downto 0);
    inbound_frame_end : in  std_logic;
    inbound_available : in  std_logic;

    outbound_write     : out std_logic;
    outbound_data      : out std_logic_vector(7 downto 0);
    outbound_frame_end : out std_logic := '0';
    outbound_available : in  std_logic;

    -- Read map
    INIT_READ_MAP : in  std_logic_vector(READ_BYTES*8-1 downto 0);
    read_map      : out std_logic_vector(READ_BYTES*8-1 downto 0);

    -- Write map
    write_map : in std_logic_vector(WRITE_BYTES*8-1 downto 0)

    );
end entity comms_register_map_masked;

architecture behave of comms_register_map_masked is

  -- Map internal signals
  signal int_read_map : std_logic_vector(READ_BYTES*2*8-1 downto 0) := (others => '0');
  signal committed_read_map : std_logic_vector(READ_BYTES*8-1 downto 0)  := (others => '0');
  signal int_write_map                    : std_logic_vector(WRITE_BYTES*8-1 downto 0) := (others => '0');

  -- simple copy state machine
  type state_type is (
    INIT,
    STREAM_READ,
    COMMIT_READ,
    LATCH_WRITE,
    STREAM_WRITE
    );

  signal state       : state_type            := INIT;
  signal packet_size : unsigned(15 downto 0) := (others => '0');
  
begin

  -- map connections
  read_map <= committed_read_map;

  -- read / write controls
  outbound_write <= '1' when state = STREAM_WRITE else '0';

  main : process(clk)
  begin
    if (rising_edge(clk)) then
      
      if (sync_reset = '1') then

        state <= INIT;
        
      else
        
        case state is
          when INIT =>

            -- Wait for new packet
            if (inbound_available = '1') then

              -- Reset the stream counter and start receiving
              packet_size <= to_unsigned(0, 16);
              state       <= STREAM_READ;

            end if;

          when STREAM_READ =>

            -- Increment the packet size while more data
            -- is available, until frame end
            if (inbound_available = '1') then

              packet_size <= packet_size + 1;

              if (inbound_frame_end = '1') then

                state       <= COMMIT_READ;
                packet_size <= to_unsigned(WRITE_BYTES, 16) - 1;

                -- Throw the packet away if the length /= READ_BYTES
                if (packet_size /= (to_unsigned(READ_BYTES * 2, 16) - 1)) then
                  state <= INIT;
                end if;

              end if;
              
            end if;

          when COMMIT_READ =>
            state <= LATCH_WRITE;

          when LATCH_WRITE =>
            state <= STREAM_WRITE;

          when STREAM_WRITE =>

            if (outbound_available = '1') then

              packet_size <= packet_size - 1;

              if (packet_size = to_unsigned(1, 16)) then
                outbound_frame_end <= '1';
              end if;

              if (packet_size = to_unsigned(0, 16)) then
                outbound_frame_end <= '0';
                state              <= INIT;
              end if;
              
            end if;
            
          when others =>
            state <= INIT;
            
        end case;

      end if;
    end if;
  end process main;

  inbound_read <= '1' when state = STREAM_READ else
                  '0';

  read_process : process(clk)
  begin
    if (rising_edge(clk)) then

      if (sync_reset = '1') then

        -- Initialise the read map
        committed_read_map <= INIT_READ_MAP;

      else
        
        if ( (state = STREAM_READ) and (inbound_available = '1') ) then

          int_read_map(READ_BYTES*2*8-1 downto 8) <= int_read_map(READ_BYTES*2*8-9 downto 0);
          int_read_map(7 downto 0)              <= inbound_data;

        elsif (state = COMMIT_READ) then

          committed_read_map <= (committed_read_map and not(int_read_map(READ_BYTES*2*8-1 downto READ_BYTES*8))) or
                                (int_read_map(READ_BYTES*8-1 downto 0) and int_read_map(READ_BYTES*2*8-1 downto READ_BYTES*8));

        end if;

      end if;
    end if;
  end process;

  outbound_write <= '1' when state = STREAM_WRITE else '0';
  outbound_data  <= int_write_map(WRITE_BYTES*8-1 downto WRITE_BYTES*8-8);

  write_process : process(clk)
  begin
    if (rising_edge(clk)) then
      if ((state = STREAM_WRITE) and (outbound_available = '1')) then
        int_write_map(WRITE_BYTES*8-1 downto 8) <= int_write_map(WRITE_BYTES*8-9 downto 0);
      else
        int_write_map <= write_map;
      end if;
    end if;
  end process;

end architecture behave;
