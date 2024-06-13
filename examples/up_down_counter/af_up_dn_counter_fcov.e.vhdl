-- DUT file: ../examples/af_ud_counter/dut_src/af_up_dn_counter.vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use std.textio.all;
-- Adding OSVVM support below 
library osvvm;
context osvvm.OsvvmContext;
use ieee.numeric_std_unsigned.all;

entity af_up_dn_counter_fcov is
  port (
    -- All DUT ports declared as inputs in FCOV model
    i_clk : in std_logic;
    i_rst_n : in std_logic;
    i_up_or_down : in std_logic;
    o_count : in std_logic_vector (7 downto 0)
    -- End of DUT ports declared in FCOV model
  );

end entity af_up_dn_counter_fcov;
