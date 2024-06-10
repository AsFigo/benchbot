import yaml
from token_test import *
import os
import argparse
import pprint
import os.path

verbose = True
def afParseArgs():
    afPsr = argparse.ArgumentParser()
    afPsr.add_argument('-i', '--input', 
        help='Input VHDL file', required=True)
    afPsr.add_argument('--osvvm', action='store_true', 
        help='Enables OSVVM Framework support ', required=False)

    return afPsr.parse_args()

class afPortInfoC():
  pName : str
  pDir : str
  pType : str
  pWidth : int
  def __init__(self, pName, pDir, pType, pWidth):
    self.pName = pName
    self.pDir = pDir
    self.pType = pType
    self.pWidth = pWidth

  def __str__(self):
    return f"{self.pName}, {self.pDir}, {self.pType}, {self.pWidth}"
  def __repr__(self):
    return str(self)

afPortsGlbL = []

def afExtractPortsInfo(lvMdl):
  global afPortsGlbL

  for iPort in lvMdl.port:
    lvCurPName = iPort[0]
    lvCurPDir = iPort[1]
    lvCurPType = iPort[2]
    lvCurPWidth = iPort[3]
    lvCurPortInfo = afPortInfoC(
        lvCurPName,
        lvCurPDir,
        lvCurPType,
        lvCurPWidth)
    afPortsGlbL.append(lvCurPortInfo)

  ymlOpFptr = open ('dut.yml', 'w')
  yaml.dump(afPortsGlbL, ymlOpFptr)

def afDeclareDutPorts():
  global afPortsGlbL

  lvCodeS = "  -- DUT ports declared as local sigals in TB\n"
  for iPort in afPortsGlbL:
    lvCodeS += "  signal "
    lvCodeS += iPort.pName + " : "
    lvCodeS += iPort.pType
    if (iPort.pWidth > 1):
      lvCodeS += f" ({iPort.pWidth-1} downto 0)"
    lvCodeS += ";\n"
  lvCodeS += "  -- End of DUT ports declared as local sigals in TB\n"
  return (lvCodeS)

def afTestcaseEnt():
  global afPortsGlbL

  lvCodeS = "  -- DUT ports declared as opposite direction in testcase\n"
  for iPort in afPortsGlbL:
    lvCodeS += "  signal "
    lvCodeS += iPort.pName + " : "
    lvCodeS += iPort.pType
    if (iPort.pWidth > 1):
      lvCodeS += f" ({iPort.pWidth-1} downto 0)"
    lvCodeS += ";\n"
  lvCodeS += "  -- End of DUT ports declared in testcase\n"
  return (lvCodeS)

def afInstantiateTest():
  global afPortsGlbL

  lvCodeS =  "  -- Generic Test instantiation\n"
  lvCodeS += "  -- DUT specific test code will go in the\n"
  lvCodeS += "  -- architecture of this generic testcase\n"
  lvCodeS += "  u_testcase : entity work.testcase\n"
  lvNumPorts = 0
  lvCodeS += "    port map (\n"
  lvCodeS += f"      o_test_done \t => test_done,\n"
  lvPortSeparator = ','
  for lvIdx, iPort in enumerate(afPortsGlbL):
    if lvIdx == len(afPortsGlbL) - 1:
      lvPortSeparator = ''

    lvCurPName = iPort.pName
    lvCodeS += f"      {lvCurPName} \t => {lvCurPName}{lvPortSeparator}\n"
  lvCodeS += f"    );\n"
  return (lvCodeS)


def afAddSimUtil():

  lvCodeS = "  -- SIM util instantiation\n"
  lvCodeS += "  u_af_sim_util : entity work.af_sim_util\n"
  lvCodeS += "    port map (\n"
  lvCodeS += f"      i_rst_n \t => osvvm_rst_n,\n"
  lvCodeS += f"      WDOG_TIMEOUT_MS \t => WDOG_TIMEOUT_MS,\n"
  lvCodeS += f"      o_test_done \t => test_done\n"
  lvCodeS += f"    );\n"
  return (lvCodeS)


def afInstantiateDUT():
  global afPortsGlbL

  lvNumPorts = 0
  lvPortS = "    port map (\n"
  lvPortSeparator = ','
  for lvIdx, iPort in enumerate(afPortsGlbL):
    if lvIdx == len(afPortsGlbL) - 1:
      lvPortSeparator = ''

    lvCurPName = iPort.pName
    lvPortS += f"      {lvCurPName} \t => {lvCurPName}{lvPortSeparator}\n"
  lvPortS += f"    );\n"
  return (lvPortS)

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


def pyVhGArch(lvMdl, lvTbName, lvOsvvmEn):
  afTbArchFp = open(f"{lvTbName}.a.vhdl",'w')
  lvDutName = lvTbName.replace('tb_', '', 1)
  afExtractPortsInfo(lvMdl)
  lvDutPortsDeclS = afDeclareDutPorts()
  lvArchS = ""
  lvArchS += afAddArchTemplate(lvTbName)
  lvArchS += lvDutPortsDeclS
  lvArchS += "begin\n"
  lvArchS += "  -- TBD - TODO\n"
  lvArchS += "  -- TODO: Connect DUT's clock to osvvm_clk\n"
  lvArchS += "  -- TODO: Connect DUT's reset to osvvm_rst_n\n"
  lvArchS += "  -- DUT instantiation\n"
  lvArchS += "  u_" + lvDutName + " : entity work."
  lvArchS += lvDutName + "\n"
  lvArchS += afHandleGenerics(lvMdl)
  lvArchS += afInstantiateDUT()
  lvArchS += afInstantiateTest()
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


def pyVhGLibHdr(lvMdl, lvTbName, lvOsvvmEn):
  lvLibL = []
  # generate header
  for iLib in lvMdl.lib:
    lvLibL.append(iLib.lower())
  #remove duplicates from the Library list
  lvTmpL = [idx for idx, val in enumerate(lvLibL) if val in lvLibL[:idx]]
 
  # excluding duplicate indices from other list
  lvFinalLibL = [ele for idx, ele in enumerate(lvLibL) if idx not in lvTmpL]

  lvLibHdrS = '-- Generated using Python Parser for VHDL\n\n'
  for iLib in lvFinalLibL:
    if "." not in iLib:
      lvLibHdrS += f"library {iLib};\n"
    else:
      lvLibHdrS += f"use {iLib};\n"     
  if ('numeric_std' not in lvLibHdrS):
    lvLibHdrS += "use ieee.numeric_std.all;\n"
  if ('std.textio' not in lvLibHdrS):
    lvLibHdrS += "use std.textio.all;\n"

  if (lvOsvvmEn):
    lvLibHdrS += "-- User enabled --osvvm option \n"
    lvLibHdrS += "-- Adding OSVVM support below \n"
    lvLibHdrS += "library osvvm;\n"
    lvLibHdrS += "context osvvm.OsvvmContext;\n"
  return (lvLibHdrS)

def pyVhGEnt(lvMdl, lvTbName, lvOsvvmEn):
  afTbEntFp = open(f"{lvTbName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvMdl, lvTbName, lvOsvvmEn)
  lvEntS += f"\nentity {lvTbName} is\n"
  lvEntS += f"\nend entity {lvTbName};\n"
  afTbEntFp.write(lvEntS)
  afTbEntFp.close()

def afSimUtilEnt(lvMdl, lvTbName, lvOsvvmEn):
  lvSimEntName = 'af_tb_sim_util'
  afSimEntFp = open(f"{lvSimEntName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvMdl, lvTbName, lvOsvvmEn)
  lvEntS += f"\nentity {lvSimEntName} is\n"
  lvEntS += f"  port (\n"
  lvEntS += f"    i_rst_n : in std_logic;\n"
  lvEntS += f"    i_test_done : in integer_barrier\n"
  lvEntS += f"  );\n"
  lvEntS += f"\nend entity {lvSimEntName};\n"
  afSimEntFp.write(lvEntS)
  afSimEntFp.close()

def afSimUtilArch(lvMdl, lvTbName, lvOsvvmEn):
  lvMarkerS = "  ------------------------------------------------------------\n"
  lvSimArchName = 'af_tb_sim_util'
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


def pyVhG():
  afPsr = afParseArgs()
  if (not os.path.isfile(afPsr.input)):
    print ("Input VHDL file not found: ", afPsr.input)
    print ("Check file name, path and extension")
    exit(1)

  lvOsvvmEn = afPsr.osvvm
  afParsedModel = parse_vhdl(afPsr.input, True)
  afTbName = f"tb_{afParsedModel.data}"
  pyVhGEnt(afParsedModel, afTbName, lvOsvvmEn)
  pyVhGArch(afParsedModel, afTbName, lvOsvvmEn)
  afSimUtilEnt(afParsedModel, afTbName, lvOsvvmEn)
  afSimUtilArch(afParsedModel, afTbName, lvOsvvmEn)


pyVhG()


