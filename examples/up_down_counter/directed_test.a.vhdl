
architecture directed_test of testcase is
  signal SB_builtin : osvvm.ScoreboardPkg_int.ScoreBoardIDType;
  begin

    init : process
    begin
      SB_builtin <= NewID("BUILTIN_SBRD");
      SetLogEnable(PASSED, TRUE);
      TranscriptOpen;
      SetTranscriptMirror(TRUE);
      wait for 0 ns;
      wait for 0 ns;
      log("A default scoreboard of int type is now ready to use");
      wait;
    end process init;

    stim : process
    begin
      WaitForClock(i_clk, 10);
      -- add your stimulus here

      -- Indicate test_done from testcase
      WaitForBarrier(o_test_done);
      wait;
    end process stim;

end architecture directed_test;
