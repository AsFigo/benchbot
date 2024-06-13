import yaml
import os
import argparse

verbose = True
def afParseArgs():
    afPsr = argparse.ArgumentParser()
    afPsr.add_argument('-y', '--yaml', 
        help='Input YAML file', required=True)

    return afPsr.parse_args()

def afDeclareDutPorts(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']

  lvCodeS = "  -- DUT ports declared as local sigals in TB\n"
  for iPort in lvPortsInfoL:
    lvCodeS += "  signal "
    lvCodeS += iPort['pName'] + " : "
    lvCodeS += iPort['pType']
    if (iPort['pWidth'] > 1):
      lvCodeS += f" ({iPort['pWidth']-1} downto 0)"
    lvCodeS += ";\n"
  lvCodeS += "  -- End of DUT ports declared as local sigals in TB\n"
  return (lvCodeS)


def afCreateSimDir(lvPortsInfoD):
  lvSimDirName = 'sim_dir'
  lvTbName = 'tb_' + lvPortsInfoD['entity']
  lvTbEntFName = '../' + lvTbName + '.e.vhdl'
  lvTbArchFName = '../' + lvTbName + '.a.vhdl'
  lvFcovName = lvPortsInfoD['entity'] + '_fcov'
  lvFcovEntFName = '../' + lvFcovName + '.e.vhdl'
  lvFcovArchFName = '../' + lvFcovName + '.a.vhdl'

  os.makedirs(lvSimDirName, exist_ok=True)
  lvTbFlistName = lvSimDirName + '/tb.f'
  lvTbFlistPtr = open (lvTbFlistName, 'w')
  lvTbFlistPtr.write('../testcase.e.vhdl\n')
  lvTbFlistPtr.write('../af_sim_util.e.vhdl\n')
  lvTbFlistPtr.write('../af_sim_util.a.vhdl\n')
  lvTbFlistPtr.write(lvFcovEntFName + '\n')
  lvTbFlistPtr.write(lvFcovArchFName + '\n')
  lvTbFlistPtr.write(lvTbEntFName + '\n')
  lvTbFlistPtr.write(lvTbArchFName + '\n')
  lvTbFlistPtr.write('../directed_test.a.vhdl\n')
  lvTbFlistPtr.write('../directed_test.a.vhdl\n')
  lvTbFlistPtr.close()


def afTestcaseEnt(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']
  lvTstName = 'testcase'
  afTstEntFp = open(f"{lvTstName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvPortsInfoD)
  lvEntS += "use osvvm.ScoreboardPkg_int.all;\n"

  lvEntS += f"\nentity {lvTstName} is\n"
  lvEntS += f"  port (\n"
  lvEntS += "    -- test_done is an indication from testcase\n"
  lvEntS += "    o_test_done : out integer_barrier;\n"


  lvClkD = next((item for item in lvPortsInfoL if item["pKind"] == "clk"), None)
  lvRstD = next((item for item in lvPortsInfoL if item["pKind"] == "rst"), None)

  lvEntS += "    -- DUT ports declared as opposite direction in testcase\n"
  lvEntS += "    -- except for clock and reset\n"
  lvPortSepS = ';\n'
  for lvIdx, iPort in enumerate(lvPortsInfoL):
    if lvIdx == len(lvPortsInfoL) - 1:
      lvPortSepS = '\n'

    lvEntS += '    ' + iPort['pName'] + " : "
    lvDirS = 'in '

    lvSwapPortDir = True
    if (iPort['pKind'] in ['clk', 'rst']):
      lvSwapPortDir = False

    if (lvSwapPortDir and iPort['pDir'].strip() == 'in'):
      lvDirS = 'out '

    lvEntS += lvDirS
    lvEntS += iPort['pType']
    if (iPort['pWidth'] > 1):
      lvEntS += f" ({iPort['pWidth']-1} downto 0)"
    lvEntS += lvPortSepS

  lvEntS += "    -- End of DUT ports declared in testcase\n"
  lvEntS += f"  );\n"
  lvEntS += f"\nend entity {lvTstName};\n"
  afTstEntFp.write(lvEntS)
  afTstEntFp.close()

def afTestcaseArch(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']
  lvTstName = 'directed_test'
  afTstArchFp = open(f"{lvTstName}.a.vhdl",'w')
  lvArchS = f"\narchitecture {lvTstName} of testcase is\n"
  lvArchS += "  signal SB_builtin : osvvm.ScoreboardPkg_int.ScoreBoardIDType;\n"
  lvArchS += "  begin\n\n"
  lvArchS += "    init : process\n"
  lvArchS += "    begin\n"
  lvArchS += "      SB_builtin <= NewID(\"BUILTIN_SBRD\");\n"
  lvArchS += "      SetLogEnable(PASSED, TRUE);\n"
  lvArchS += "      TranscriptOpen;\n"
  lvArchS += "      SetTranscriptMirror(TRUE);\n" 
  lvArchS += "      wait for 0 ns;\n"
  lvArchS += "      wait for 0 ns;\n"
  lvArchS += "      log(\"A default scoreboard of int type is now ready to use\");\n"
  lvArchS += "      wait;\n"
  lvArchS += "    end process init;\n\n"

  lvArchS += "    stim : process\n"
  lvArchS += "    begin\n"


  lvClkD = next((item for item in lvPortsInfoL if item["pKind"] == "clk"), None)
  if (lvClkD is not None):
    lvClkName = lvClkD['pName']
    lvArchS += f"      WaitForClock({lvClkName}, 10);\n"

  lvArchS += "      -- add your stimulus here\n\n"
  lvArchS += "      -- Indicate test_done from testcase\n"
  lvArchS += "      WaitForBarrier(o_test_done);\n"
  lvArchS += "      wait;\n"
  lvArchS += "    end process stim;\n"

  lvArchS += f"\nend architecture {lvTstName};\n"
  afTstArchFp.write(lvArchS)
  afTstArchFp.close()

def afGenFcovEnt(lvPortsInfoD):
  lvFcovName = lvPortsInfoD['entity'] + '_fcov'
  lvPortsInfoL = lvPortsInfoD['ports']
  afFcovEntFp = open(f"{lvFcovName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvPortsInfoD)
  lvEntS += "use ieee.numeric_std_unsigned.all;\n"

  lvEntS += f"\nentity {lvFcovName} is\n"
  lvEntS += f"  port (\n"

  lvClkD = next((item for item in lvPortsInfoL if item["pKind"] == "clk"), None)
  lvRstD = next((item for item in lvPortsInfoL if item["pKind"] == "rst"), None)

  lvEntS += "    -- All DUT ports declared as inputs in FCOV model\n"
  lvPortSepS = ';\n'
  for lvIdx, iPort in enumerate(lvPortsInfoL):
    if lvIdx == len(lvPortsInfoL) - 1:
      lvPortSepS = '\n'

    lvEntS += '    ' + iPort['pName'] + " : "
    lvDirS = 'in '

    lvEntS += lvDirS
    lvEntS += iPort['pType']
    if (iPort['pWidth'] > 1):
      lvEntS += f" ({iPort['pWidth']-1} downto 0)"
    lvEntS += lvPortSepS

  lvEntS += "    -- End of DUT ports declared in FCOV model\n"
  lvEntS += f"  );\n"
  lvEntS += f"\nend entity {lvFcovName};\n"
  afFcovEntFp.write(lvEntS)
  afFcovEntFp.close()


def afGenFcovArch(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']
  lvFcovName = lvPortsInfoD['entity'] + '_fcov'
  lvFcovArchFp = open(f"{lvFcovName}.a.vhdl",'w')
  lvPortsInfoL = lvPortsInfoD['ports']

  lvArchS = f"\narchitecture verif of {lvFcovName} is\n"
  lvArchS += "  constant FCOV_AUTO_BIN_MAX : integer := 64;\n"
  lvArchS += "  constant FCOV_RST_TGL_MIN : integer := 3;\n"
  lvArchS += "  signal i_test_done : integer_barrier;\n"
  lvArchS += "  signal afFcovRes : real;\n"
  for iPort in lvPortsInfoL:
    lvCurPName = iPort['pName']
    lvCovID = lvCurPName + '_CID'
    lvArchS += f"  signal {lvCovID} : CoverageIdType;\n"
  lvArchS += "  begin\n\n"
  lvArchS += "    init_cov_model : process\n"
  lvArchS += "    begin\n"
  for iPort in lvPortsInfoL:
    lvCurPName = iPort['pName']
    lvCovID = lvCurPName + '_CID'
    lvArchS += f"      {lvCovID} <= NewID(\"{lvCovID}\");\n"

  lvArchS += "      wait for 0 ns;\n"
  lvArchS += "      wait for 0 ns;\n"
  for iPort in lvPortsInfoL:
    lvCurPName = iPort['pName']
    lvCovID = lvCurPName + '_CID'
    if (iPort['pWidth'] == 1):
      lvArchS += f"      -- single bit signal, so add GenBin(0,1)\n"
      lvArchS += f"      AddBins({lvCovID}, GenBin(0,1));\n"
    else:
      lvArchS += f"      -- multi-bit signal, so add AUTO BINS\n"
      lvArchS += f"      AddBins({lvCovID}, GenBin(\n"
      lvArchS += f"        Min => {lvCurPName}\'low,\n"
      lvArchS += f"        Max => {lvCurPName}\'high,\n"
      lvArchS += f"        NumBin => FCOV_AUTO_BIN_MAX\n"
      lvArchS += f"      ));\n"

  lvArchS += "    end process init_cov_model;\n\n"

  lvArchS += "    -- add your extra FCOV model here\n\n"

  for iPort in lvPortsInfoL:
    lvCurPName = iPort['pName']
    lvCovID = lvCurPName + '_CID'
    lvArchS += f"    -- Sampling {lvCurPName} at every value change\n"
    lvArchS += f"    {lvCovID}_sample : postponed process ({lvCurPName}) is\n"
    lvArchS += "    begin\n"
    lvArchS += "      if (now > 1 ns) then\n"
    lvArchS += f"       ICover(ID => {lvCovID},\n"
    lvArchS += f"         CovPoint => to_integer({lvCurPName}));\n"
    lvArchS += "      end if;\n"
    lvArchS += f"    end process {lvCovID}_sample;\n\n"

  lvArchS += "    fcov_report : process\n"
  lvArchS += "    begin\n"
  lvArchS += "      -- Wait for test_done from testcase\n"
  lvArchS += "      WaitForBarrier(i_test_done);\n"
  for iPort in lvPortsInfoL:
    lvCurPName = iPort['pName']
    lvCovID = lvCurPName + '_CID'
    lvArchS += f"      WriteBin({lvCovID});\n"

  lvArchS += "      afFcovRes <= GetCov(100.0);\n"
  lvArchS += "      log(\"FCOV achieved in this run: \" & to_string(afFcovRes, \"%.2f\") & \"%\");\n"

  lvArchS += "      wait;\n"
  lvArchS += "    end process fcov_report;\n"

  lvArchS += f"\nend architecture verif;\n"
  lvFcovArchFp.write(lvArchS)
  lvFcovArchFp.close()


def afInstantiateTest(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']

  lvCodeS =  "\n\n  -- Generic Test instantiation\n"
  lvCodeS += "  -- DUT specific test code will go in the\n"
  lvCodeS += "  -- architecture of this generic testcase\n"
  lvCodeS += "  u_testcase : entity work.testcase\n"
  lvNumPorts = 0
  lvCodeS += "    port map (\n"
  lvCodeS += f"      o_test_done \t => test_done,\n"
  lvPortSeparator = ','
  for lvIdx, iPort in enumerate(lvPortsInfoL):
    if lvIdx == len(lvPortsInfoL) - 1:
      lvPortSeparator = ''

    lvCurPName = iPort['pName']
    lvCodeS += f"      {lvCurPName} \t => {lvCurPName}{lvPortSeparator}\n"
  lvCodeS += f"    );\n"
  return (lvCodeS)


def afAddSimUtil():

  lvCodeS = "  -- SIM util instantiation\n"
  lvCodeS += "  u_af_sim_util : entity work.af_sim_util\n"
  lvCodeS += "    generic map (\n"
  lvCodeS += f"      WDOG_TIMEOUT_MS \t => WDOG_TIMEOUT_MS)\n"
  lvCodeS += "    port map (\n"
  lvCodeS += f"      i_rst_n \t => osvvm_rst_n,\n"
  lvCodeS += f"      i_test_done \t => test_done\n"
  lvCodeS += f"    );\n"
  return (lvCodeS)


def afInstantiateDUT(lvPortsInfoD):
  lvPortsInfoL = lvPortsInfoD['ports']

  lvPortS = "    port map (\n"
  lvNumPorts = 0
  lvPortSeparator = ','
  for lvIdx, iPort in enumerate(lvPortsInfoL):
    if lvIdx == len(lvPortsInfoL) - 1:
      lvPortSeparator = ''

    lvCurPName = iPort['pName']
    lvPortS += f"      {lvCurPName} \t => {lvCurPName}{lvPortSeparator}\n"
  lvPortS += f"    );\n"
  return (lvPortS)

def afInstantiateFCOV(lvPortsInfoD):
  lvFcovName = lvPortsInfoD['entity'] + '_fcov'
  lvCodeS = "  -- FCOV model is below\n"
  lvCodeS += "  -- FCOV instantiation\n"
  lvCodeS += "  u_" + lvFcovName + " : entity work."
  lvCodeS += lvFcovName + "\n"
  lvPortsInfoL = lvPortsInfoD['ports']

  lvCodeS += "    port map (\n"
  lvNumPorts = 0
  lvCodeSeparator = ','
  for lvIdx, iPort in enumerate(lvPortsInfoL):
    if lvIdx == len(lvPortsInfoL) - 1:
      lvCodeSeparator = ''

    lvCurPName = iPort['pName']
    lvCodeS += f"      {lvCurPName} \t => {lvCurPName}{lvCodeSeparator}\n"
  lvCodeS += f"    );\n"
  return (lvCodeS)



def afAddArchTemplate(lvTbName):
  lvArchTmplS = ""
  lvArchTmplS += f"architecture func of {lvTbName} is\n"
  lvArchTmplS += "  constant CLK_PERIOD : time := 10 ns ;\n" 
  lvArchTmplS += "  constant NUM_RST_CYC : positive := 10;\n" 
  lvArchTmplS += "  constant RST_TPD  : time := 2 ns ;\n" 
  lvArchTmplS += "  -- WDOG_TIMEOUT_MS  used via barrier in Watchdog\n"
  lvArchTmplS += "  constant WDOG_TIMEOUT_MS : time := 1 ms;\n\n" 
  lvArchTmplS += "\n  -- Default clock from pyVhG below\n"
  lvArchTmplS += "  -- Connect this to DUT\'s clock input\n"
  lvArchTmplS += "  signal osvvm_clk  : std_logic;\n" 
  lvArchTmplS += "\n  -- Default reset from pyVhG below\n"
  lvArchTmplS += "  -- Connect this to DUT\'s reset input\n"
  lvArchTmplS += "  -- Note: this is active low reset in pyVhG\n"
  lvArchTmplS += "  signal osvvm_rst_n  : std_logic := '0';\n\n" 
  lvArchTmplS += "  -- TEST_DONE used as barrier in Watchdog\n"
  lvArchTmplS += "  signal test_done  : integer_barrier := 1;\n\n" 

  return lvArchTmplS


def pyVhGArch(lvPortsInfoD):
  lvDutName = lvPortsInfoD['entity']
  lvPortDicts = lvPortsInfoD['ports']
  lvClkD = next((item for item in lvPortDicts if item["pKind"] == "clk"), None)
  lvRstD = next((item for item in lvPortDicts if item["pKind"] == "rst"), None)

  lvTbName = 'tb_' + lvDutName
  afTbArchFp = open(f"{lvTbName}.a.vhdl",'w')
  lvDutPortsDeclS = afDeclareDutPorts(lvPortsInfoD)
  lvArchS = ""
  lvArchS += afAddArchTemplate(lvTbName)
  lvArchS += lvDutPortsDeclS
  lvArchS += "begin\n"
  lvArchS += "  -- TBD - TODO\n"
  lvArchS += "  -- TODO: Connect DUT's clock to osvvm_clk\n"
  if (lvClkD is not None):
    lvArchS += "  " + lvClkD['pName'] + " <= osvvm_clk;\n"
  lvArchS += "  -- TODO: Connect DUT's reset to osvvm_rst_n\n"
  if (lvRstD is not None):
    lvArchS += "  " + lvRstD['pName'] + " <= osvvm_rst_n;\n"
  lvArchS += "  -- DUT instantiation\n"
  lvArchS += "  u_" + lvDutName + " : entity work."
  lvArchS += lvDutName + "\n"
  lvArchS += afInstantiateDUT(lvPortsInfoD)
  '''
  lvArchS += afHandleGenerics(lvMdl)
  '''
  lvArchS += afInstantiateTest(lvPortsInfoD)
  #lvArchS += afInstantiateFCOV(lvPortsInfoD)
  lvArchS += afAddSimUtil()
  lvArchS += afOsvvmClkGen()
  lvArchS += afOsvvmRstGen()
  lvArchS += f"\nend architecture func;\n"
  afTbArchFp.write(lvArchS)
  afTbArchFp.close()


def afOsvvmClkGen():
  lvClkGenS = """
  ------------------------------------------------------------
  -- Clock Generation
  -- Default clock from pyVhG below
  -- Connect this to DUT\'s clock input
  -- Use CLK_PERIOD to adjust as per your design frequency
  ------------------------------------------------------------
  Osvvm.TbUtilPkg.CreateClock ( 
    Clk        => osvvm_clk, 
    Period     => CLK_PERIOD 
    )  ; 

  """
  return lvClkGenS

def afOsvvmRstGen():
  lvRstGenS = """
  ------------------------------------------------------------
  -- Reset Generation 
  -- Default reset from pyVhG below"
  -- Connect this to DUT\'s reset input"
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

  """
  return lvRstGenS


def pyVhGLibHdr(lvPortsInfoD):
  lvLibHdrS = lvPortsInfoD['libraries']
  lvLibHdrS = lvLibHdrS.replace('#', '--')
  lvLibHdrS += "-- Adding OSVVM support below \n"
  lvLibHdrS += "library osvvm;\n"
  lvLibHdrS += "context osvvm.OsvvmContext;\n"
  return (lvLibHdrS)

def pyVhGEnt(lvPortsInfoD):
  lvTbName = 'tb_' + lvPortsInfoD['entity']
  afTbEntFp = open(f"{lvTbName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvPortsInfoD)
  lvEntS += f"\nentity {lvTbName} is\n"
  lvEntS += f"\nend entity {lvTbName};\n"
  afTbEntFp.write(lvEntS)
  afTbEntFp.close()

def afSimUtilEnt(lvPortsInfoD):
  lvSimEntName = 'af_sim_util'
  afSimEntFp = open(f"{lvSimEntName}.e.vhdl",'w')

  lvEntS = pyVhGLibHdr(lvPortsInfoD)
  lvEntS += f"\nentity {lvSimEntName} is\n"
  lvEntS += "  generic (WDOG_TIMEOUT_MS : time := 1 ms);\n"
  lvEntS += f"  port (\n"
  lvEntS += f"    i_rst_n : in std_logic;\n"
  lvEntS += f"    i_test_done : in integer_barrier\n"
  lvEntS += f"  );\n"
  lvEntS += f"\nend entity {lvSimEntName};\n"
  afSimEntFp.write(lvEntS)
  afSimEntFp.close()

def afSimUtilArch():
  lvMarkerS = "  ------------------------------------------------------------\n"
  lvSimArchName = 'af_sim_util'
  afSimArchFp = open(f"{lvSimArchName}.a.vhdl",'w')
  lvArchS = ""
  lvArchS += f"\narchitecture builtin of {lvSimArchName} is\n"
  lvArchS += "  signal TestDone : integer_barrier;\n"
  lvArchS += "begin\n"
  lvArchS += lvMarkerS
  lvArchS += "  -- ControlProc\n"
  lvArchS += "  -- Set up AlertLog and wait for end of test\n"
  lvArchS += lvMarkerS
  lvArchS += "  controlProc : process\n"
  lvArchS += "  begin\n"
  lvArchS += "    -- Wait for testbench initialization\n"
  lvArchS += "    wait for 0 ns ; wait for 0 ns;\n"
  lvArchS += "    -- Wait for Design Reset\n"
  lvArchS += "    wait until i_rst_n = '1';\n"
  lvArchS += "    ClearAlerts;\n"

  lvArchS += "    -- Wait for test to finish\n"
  lvArchS += "    WaitForBarrier(TestDone, WDOG_TIMEOUT_MS);\n"
  lvArchS += "    AlertIf(now >= WDOG_TIMEOUT_MS, "
  lvArchS += "\"Test finished due to timeout\");\n"
  lvArchS += "    AlertIf(GetAffirmCount < 1, "
  lvArchS += "\"Test is not Self-Checking\");\n"
  lvArchS += "    TranscriptClose;\n"
  lvArchS += "    EndOfTestReports;\n"
  lvArchS += "    EndOfTestSummary(ReportAll => TRUE);\n" 
  lvArchS += "    std.env.stop;\n"
  lvArchS += "    wait;\n"
  lvArchS += "  end process controlProc;\n"

  lvArchS += f"\nend architecture builtin;\n"
  afSimArchFp.write(lvArchS)
  afSimArchFp.close()

def afParseYaml(lvInpYaml):
  lvInpYmlF = open (lvInpYaml, 'r')
  lvPortsInfoD = yaml.safe_load(lvInpYmlF)
  return (lvPortsInfoD)

def main():
  afPsr = afParseArgs()
  if (not os.path.isfile(afPsr.yaml)):
    print ("Input YAML file not found: ", afPsr.yaml)
    print ("Check file name, path and extension")
    exit(1)

  lvPortsInfoD = afParseYaml(afPsr.yaml)
  pyVhGEnt(lvPortsInfoD)
  pyVhGArch(lvPortsInfoD)
  afSimUtilEnt(lvPortsInfoD)
  afSimUtilArch()
  afGenFcovEnt(lvPortsInfoD)
  afGenFcovArch(lvPortsInfoD)
  afTestcaseEnt(lvPortsInfoD)
  afTestcaseArch(lvPortsInfoD)
  afCreateSimDir(lvPortsInfoD)

if __name__ == "__main__":
  main()


def afHandleGenerics(lvMdl):

  lvGenericS = ""
  if len(lvMdl.generic) > 0:
    lvGenericS = "generic map (\n"
    for iGen in decoded.generic[:-1]:
      lvGenericS += f"{iGen[0]} => {iGen[0]}\n"
    iGen = decoded.generic[-1]
    lvGenericS += f"{iGen[0]} => {iGen[0]}\n"
    lvGenericS += f");\n"
    lvGenericS += "    )\n"
  return (lvGenericS)
