library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;

entity af_up_dn_counter is
  Port ( i_clk : in  std_logic;     -- input clock
         i_rst_n : in std_logic;
         i_up_or_down : in  std_logic;    
         o_count : out  std_logic_vector (7 downto 0)
       );
end af_up_dn_counter;

architecture rtl of af_up_dn_counter is
  signal int_count   : std_logic_vector (7 downto 0) := X"00";
begin

  process (i_clk)
  begin
    if (rising_edge(i_clk)) then
      if (i_rst_n = '0') then
        int_count <= X"00";
      else
        if (i_up_or_down = '1') then
          int_count <= int_count + '1';   -- counting up
        elsif (i_up_or_down = '0') then
          int_count <= int_count - '1';   -- counting down
        end if;
      end if;
    end if;
  end process;

  o_count <= int_count;

end architecture rtl;
