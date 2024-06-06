library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
-- User enabled --osvvm option 
-- Adding OSVVM support below 
library osvvm;
context osvvm.OsvvmContext;

entity testcase is
  port ( i_clk : in  std_logic;     -- input clock
         i_rst_n : in std_logic;
         i_up_or_down : out  std_logic;    
         o_test_done : out  integer_barrier;    
         o_count : in  std_logic_vector (7 downto 0)
       );
end entity testcase;

architecture directed_test of testcase is
  signal int_count   : std_logic_vector (7 downto 0) := X"00";
begin

  stim : process
  begin
    i_up_or_down <= '0';
    wait for 100 ns;
    i_up_or_down <= '1';
    wait for 100 ns;
    i_up_or_down <= '0';
    wait for 100 ns;
    i_up_or_down <= '1';
    wait for 100 ns;
    i_up_or_down <= '0';
    report "Test end";
    WaitForBarrier(o_test_done);
    
    wait;
  end process stim;
end architecture directed_test;

