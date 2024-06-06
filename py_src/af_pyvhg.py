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


def afHandlePorts():
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

def pyVhGArch(lvMdl, lvTbName, lvOsvvmEn):
  afTbArchFp = open(f"{lvTbName}.a.vhdl",'w')
  lvDutName = lvTbName.replace('tb_', '', 1)
  afExtractPortsInfo(lvMdl)
  lvDutPortsDeclS = afDeclareDutPorts()
  lvArchS = ""
  lvArchS += f"architecture func of {lvTbName} is\n"
  lvArchS += "  constant CLK_PERIOD : time := 10 ns ;\n" 
  lvArchS += "  constant NUM_RST_CYC : positive := 10;\n" 
  lvArchS += "  constant RST_TPD  : time := 2 ns ;\n" 
  lvArchS += "\n  -- Default clock from pyVhG below\n"
  lvArchS += "  -- Connect this to DUT\'s clock input\n"
  lvArchS += "  signal osvvm_clk  : std_logic;\n" 
  lvArchS += "\n  -- Default reset from pyVhG below\n"
  lvArchS += "  -- Connect this to DUT\'s reset input\n"
  lvArchS += "  -- Note: this is active low reset in pyVhG\n"
  lvArchS += "  signal osvvm_rst_n  : std_logic := '0';\n\n" 
  lvArchS += lvDutPortsDeclS
  lvArchS += "begin\n"
  lvArchS += "  -- DUT instanatiation\n"
  lvArchS += "  u_" + lvDutName + " : entity work."
  lvArchS += lvDutName + "\n"
  lvArchS += afHandleGenerics(lvMdl)
  lvArchS += afHandlePorts()
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

def afGenWdogEnt(lvMdl, lvTbName, lvOsvvmEn):
  lvWdEntName = 'af_tb_wdog'
  afWdEntFp = open(f"{lvWdEntName}.e.vhdl",'w')
  lvEntS = pyVhGLibHdr(lvMdl, lvTbName, lvOsvvmEn)
  lvEntS += f"\nentity {lvWdEntName} is\n"
  lvEntS += f"\nend entity {lvWdEntName};\n"
  afWdEntFp.write(lvEntS)
  afWdEntFp.close()

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
  afGenWdogEnt(afParsedModel, afTbName, lvOsvvmEn)


pyVhG()


