-- DUT file: ../examples/af_ud_counter/dut_src/af_up_dn_counter.vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use std.textio.all;
-- Adding OSVVM support below 
library osvvm;
context osvvm.OsvvmContext;
use osvvm.ScoreboardPkg_int.all;

entity testcase is
  port (
    -- test_done is an indication from testcase
    o_test_done : out integer_barrier;
    -- DUT ports declared as opposite direction in testcase
    -- except for clock and reset
    i_clk : in std_logic;
    i_rst_n : in std_logic;
    i_up_or_down : out std_logic;
    o_count : in std_logic_vector (7 downto 0)
    -- End of DUT ports declared in testcase
  );

end entity testcase;
