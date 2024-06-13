
architecture builtin of af_sim_util is
  signal TestDone : integer_barrier;
begin
  ------------------------------------------------------------
  -- ControlProc
  -- Set up AlertLog and wait for end of test
  ------------------------------------------------------------
  controlProc : process
  begin
    -- Wait for testbench initialization
    wait for 0 ns ; wait for 0 ns;
    -- Wait for Design Reset
    wait until i_rst_n = '1';
    ClearAlerts;
    -- Wait for test to finish
    WaitForBarrier(TestDone, WDOG_TIMEOUT_MS);
    AlertIf(now >= WDOG_TIMEOUT_MS, "Test finished due to timeout");
    AlertIf(GetAffirmCount < 1, "Test is not Self-Checking");
    TranscriptClose;
    EndOfTestReports;
    EndOfTestSummary(ReportAll => TRUE);
    std.env.stop;
    wait;
  end process controlProc;

end architecture builtin;
