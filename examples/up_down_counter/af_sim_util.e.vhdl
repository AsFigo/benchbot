-- DUT file: ../examples/af_ud_counter/dut_src/af_up_dn_counter.vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use std.textio.all;
-- Adding OSVVM support below 
library osvvm;
context osvvm.OsvvmContext;

entity af_sim_util is
  generic (WDOG_TIMEOUT_MS : time := 1 ms);
  port (
    i_rst_n : in std_logic;
    i_test_done : in integer_barrier
  );

end entity af_sim_util;
