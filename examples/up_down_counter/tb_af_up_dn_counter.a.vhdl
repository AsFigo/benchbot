architecture func of tb_af_up_dn_counter is
  constant CLK_PERIOD : time := 10 ns ;
  constant NUM_RST_CYC : positive := 10;
  constant RST_TPD  : time := 2 ns ;
  -- WDOG_TIMEOUT_MS  used via barrier in Watchdog
  constant WDOG_TIMEOUT_MS : time := 1 ms;


  -- Default clock from pyVhG below
  -- Connect this to DUT's clock input
  signal osvvm_clk  : std_logic;

  -- Default reset from pyVhG below
  -- Connect this to DUT's reset input
  -- Note: this is active low reset in pyVhG
  signal osvvm_rst_n  : std_logic := '0';

  -- TEST_DONE used as barrier in Watchdog
  signal test_done  : integer_barrier := 1;

  -- DUT ports declared as local sigals in TB
  signal i_clk : std_logic;
  signal i_rst_n : std_logic;
  signal i_up_or_down : std_logic;
  signal o_count : std_logic_vector (7 downto 0);
  -- End of DUT ports declared as local sigals in TB
begin
  -- TBD - TODO
  -- TODO: Connect DUT's clock to osvvm_clk
  i_clk <= osvvm_clk;
  -- TODO: Connect DUT's reset to osvvm_rst_n
  i_rst_n <= osvvm_rst_n;
  -- DUT instantiation
  u_af_up_dn_counter : entity work.af_up_dn_counter
    port map (
      i_clk 	 => i_clk,
      i_rst_n 	 => i_rst_n,
      i_up_or_down 	 => i_up_or_down,
      o_count 	 => o_count
    );


  -- Generic Test instantiation
  -- DUT specific test code will go in the
  -- architecture of this generic testcase
  u_testcase : entity work.testcase
    port map (
      o_test_done 	 => test_done,
      i_clk 	 => i_clk,
      i_rst_n 	 => i_rst_n,
      i_up_or_down 	 => i_up_or_down,
      o_count 	 => o_count
    );
  -- SIM util instantiation
  u_af_sim_util : entity work.af_sim_util
    generic map (
      WDOG_TIMEOUT_MS 	 => WDOG_TIMEOUT_MS)
    port map (
      i_rst_n 	 => osvvm_rst_n,
      i_test_done 	 => test_done
    );

  ------------------------------------------------------------
  -- Clock Generation
  -- Default clock from pyVhG below
  -- Connect this to DUT's clock input
  -- Use CLK_PERIOD to adjust as per your design frequency
  ------------------------------------------------------------
  Osvvm.TbUtilPkg.CreateClock ( 
    Clk        => osvvm_clk, 
    Period     => CLK_PERIOD 
    )  ; 

  
  ------------------------------------------------------------
  -- Reset Generation 
  -- Default reset from pyVhG below"
  -- Connect this to DUT's reset input"
  -- Note: this is active low reset in pyVhG"
  -- Number of reset cycles is controlled by knob: NUM_RST_CYC
  -- tPD - propagation delay, for asyncrhonous deassertion
  -- of reset pin can be achieved by using the knob: RST_TPD
  ------------------------------------------------------------
  Osvvm.TbUtilPkg.CreateReset ( 
    Reset       => osvvm_rst_n,
    ResetActive => '0',
    Clk         => osvvm_clk,
    Period      => NUM_RST_CYC * CLK_PERIOD,
    tpd         => RST_TPD
    ) ;

  
end architecture func;
