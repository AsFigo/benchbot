import yaml
from token_test import *
import os
import argparse
import os.path

verbose = True
def afParseArgs():
    afPsr = argparse.ArgumentParser()
    afPsr.add_argument('-i', '--input', 
        help='Input VHDL file', required=True)
    afPsr.add_argument('-o', '--output', 
        help='Output YAML file, default af_dut.yml', required=False)

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

  def to_dict(self):
    return {
      'pDir': self.pDir,
      'pName': self.pName,
      'pType': self.pType,
      'pKind': "ctrlData",
      'pWidth': self.pWidth
    }
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

def afClassifyPort(lvPortDictsL):
  lvModPortL = list()
  for lvPort in lvPortDictsL:
    lvPname = lvPort['pName'].strip()
    if ('clock' in lvPname):
      lvPort['pKind'] = "clk"
    if ('clk' in lvPname):
      lvPort['pKind'] = "clk"
    if ('reset' in lvPname):
      lvPort['pKind'] = "rst"
    if ('rst_n' in lvPname):
      lvPort['pKind'] = "rst"
    lvModPortL.append(lvPort)
  return (lvModPortL)
 
def afDumpYaml(lvEntName, lvLibS, lvYmlOpFname):
  global afPortsGlbL
  lvPortInfoD = dict()
  ymlOpFptr = open (lvYmlOpFname, 'w')
  # Convert the list of afPortInfoC instances to a list of dictionaries
  lvPortTmpL = [port.to_dict() for port in afPortsGlbL]  
  lvPortDictsL = afClassifyPort(lvPortTmpL)
  lvPortInfoD['entity'] = lvEntName
  lvPortInfoD['libraries'] = lvLibS
  lvPortInfoD['ports'] = lvPortDictsL
  yaml.dump(lvPortInfoD, ymlOpFptr)
  print ('YAML info is written to file: ', lvYmlOpFname)

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


def afGpinfLibHdr(lvMdl, lvVhFname):
  lvLibL = []
  # generate header
  for iLib in lvMdl.lib:
    lvLibL.append(iLib.lower())
  #remove duplicates from the Library list
  lvTmpL = [idx for idx, val in enumerate(lvLibL) if val in lvLibL[:idx]]
 
  # excluding duplicate indices from other list
  lvFinalLibL = [ele for idx, ele in enumerate(lvLibL) if idx not in lvTmpL]

  lvLibHdrS = '# Generated YAML using VHDL_Parse Parser for VHDL\n\n'
  lvLibHdrS = '# DUT file: ' + lvVhFname + '\n'
  for iLib in lvFinalLibL:
    if "." not in iLib:
      lvLibHdrS += f"library {iLib};\n"
    else:
      lvLibHdrS += f"use {iLib};\n"     
  if ('numeric_std' not in lvLibHdrS):
    lvLibHdrS += "use ieee.numeric_std.all;\n"
  if ('std.textio' not in lvLibHdrS):
    lvLibHdrS += "use std.textio.all;\n"

  return (lvLibHdrS)


def main():
  afPsr = afParseArgs()
  if (not os.path.isfile(afPsr.input)):
    print ("Input VHDL file not found: ", afPsr.input)
    print ("Check file name, path and extension")
    exit(1)

  afParsedModel = parse_vhdl(afPsr.input, True)
  lvYmlOpFname = afParsedModel.data + '.yml'
  if (afPsr.output):
    lvYmlOpFname = afPsr.output

  lvEntName = afParsedModel.data
  lvLibS = afGpinfLibHdr(afParsedModel, afPsr.input)
  afExtractPortsInfo(afParsedModel)
  afDumpYaml(lvEntName, lvLibS, lvYmlOpFname)

if __name__ == "__main__":
  main()


