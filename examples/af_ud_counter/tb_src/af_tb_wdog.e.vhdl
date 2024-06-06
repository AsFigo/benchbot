-- Generated using Python Parser for VHDL

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use std.textio.all;
-- User enabled --osvvm option 
-- Adding OSVVM support below 
library osvvm;
context osvvm.OsvvmContext;

entity af_sim_wdog is
  port (i_rst_n : in std_logic;
        i_test_done : in integer_barrier);
end entity af_sim_wdog;

architecture func of af_sim_wdog is

  signal TestDone : integer_barrier;
begin

  TestDone <= i_test_done;
------------------------------------------------------------
-- ControlProc
-- Set up AlertLog and wait for end of test
------------------------------------------------------------
  ControlProc : process
  begin

    -- Wait for testbench initialization
    wait for 0 ns ; wait for 0 ns ;

    -- Wait for Design Reset
    wait until i_rst_n = '1' ;
    ClearAlerts ;

    -- Wait for test to finish
    WaitForBarrier(TestDone, 1 ms) ;
    AlertIf(now >= 1 ms, "Test finished due to timeout") ;
    AlertIf(GetAffirmCount < 1, "Test is not Self-Checking");

    TranscriptClose;

    -- Create yaml reports for scoreboard
    -- osvvm_uart.ScoreboardPkg_Uart.WriteScoreboardYaml(FileName => GetTestName & "_sb_Uart.yml") ;
    -- EndOfTestReports ;
    std.env.stop ;
    wait ;
  end process ControlProc ;

end architecture func;

