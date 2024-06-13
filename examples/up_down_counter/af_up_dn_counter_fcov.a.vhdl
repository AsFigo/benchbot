
architecture verif of af_up_dn_counter_fcov is
  constant FCOV_AUTO_BIN_MAX : integer := 64;
  constant FCOV_RST_TGL_MIN : integer := 3;
  signal i_test_done : integer_barrier;
  signal afFcovRes : real;
  signal i_clk_CID : CoverageIdType;
  signal i_rst_n_CID : CoverageIdType;
  signal i_up_or_down_CID : CoverageIdType;
  signal o_count_CID : CoverageIdType;
  begin

    init_cov_model : process
    begin
      i_clk_CID <= NewID("i_clk_CID");
      i_rst_n_CID <= NewID("i_rst_n_CID");
      i_up_or_down_CID <= NewID("i_up_or_down_CID");
      o_count_CID <= NewID("o_count_CID");
      wait for 0 ns;
      wait for 0 ns;
      -- single bit signal, so add GenBin(0,1)
      AddBins(i_clk_CID, GenBin(0,1));
      -- single bit signal, so add GenBin(0,1)
      AddBins(i_rst_n_CID, GenBin(0,1));
      -- single bit signal, so add GenBin(0,1)
      AddBins(i_up_or_down_CID, GenBin(0,1));
      -- multi-bit signal, so add AUTO BINS
      AddBins(o_count_CID, GenBin(
        Min => o_count'low,
        Max => o_count'high,
        NumBin => FCOV_AUTO_BIN_MAX
      ));
    end process init_cov_model;

    -- add your extra FCOV model here

    -- Sampling i_clk at every value change
    i_clk_CID_sample : postponed process (i_clk) is
    begin
      if (now > 1 ns) then
       ICover(ID => i_clk_CID,
         CovPoint => to_integer(i_clk));
      end if;
    end process i_clk_CID_sample;

    -- Sampling i_rst_n at every value change
    i_rst_n_CID_sample : postponed process (i_rst_n) is
    begin
      if (now > 1 ns) then
       ICover(ID => i_rst_n_CID,
         CovPoint => to_integer(i_rst_n));
      end if;
    end process i_rst_n_CID_sample;

    -- Sampling i_up_or_down at every value change
    i_up_or_down_CID_sample : postponed process (i_up_or_down) is
    begin
      if (now > 1 ns) then
       ICover(ID => i_up_or_down_CID,
         CovPoint => to_integer(i_up_or_down));
      end if;
    end process i_up_or_down_CID_sample;

    -- Sampling o_count at every value change
    o_count_CID_sample : postponed process (o_count) is
    begin
      if (now > 1 ns) then
       ICover(ID => o_count_CID,
         CovPoint => to_integer(o_count));
      end if;
    end process o_count_CID_sample;

    fcov_report : process
    begin
      -- Wait for test_done from testcase
      WaitForBarrier(i_test_done);
      WriteBin(i_clk_CID);
      WriteBin(i_rst_n_CID);
      WriteBin(i_up_or_down_CID);
      WriteBin(o_count_CID);
      afFcovRes <= GetCov(100.0);
      log("FCOV achieved in this run: " & to_string(afFcovRes, "%.2f") & "%");
      wait;
    end process fcov_report;

end architecture verif;
