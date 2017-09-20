# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Created on November 2016

@author: mandd
"""
#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
if not 'xrange' in dir(__builtins__):
  xrange = range
#End compatibility block for Python 3----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
import numpy as np
import copy
#External Modules End--------------------------------------------------------------------------------

from PostProcessorInterfaceBaseClass import PostProcessorInterfaceBase

class ETanalysis(PostProcessorInterfaceBase):
  """ This class implements the four basic risk-importance measures
      This class inherits form the base class PostProcessorInterfaceBase and it contains three methods:
      - initialize
      - run
      - readMoreXML
  """

  def initialize(self):
    """
      Method to initialize the Interfaced Post-processor
      @ In, None
      @ Out, None

    """
    PostProcessorInterfaceBase.initialize(self)
    self.inputFormat  = 'PointSet'
    self.outputFormat = 'PointSet'

  def readMoreXML(self,xmlNode):
    """
      Function that reads elements this post-processor will use
      @ In, xmlNode, ElementTree, Xml element node
      @ Out, None
    """
    self.variables = {}
    self.target    = {}
    self.branchID = None
    self.mode = None
    self.ETvariablesList = []
    self.dynamicVariablesList = []

    for child in xmlNode:
        if child.tag == 'ETvariable':
            variableID = child.text
            self.ETvariablesList.append(variableID)
            self.variables[variableID] = {}
            if 'R0values' in child.attrib.keys():
              values = child.attrib['R0values'].split(',')
              if len(values) != 2:
                self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                  ' : attribute node R0 for XML node: ' + str(child) + ' has one or more than two values')
              try:
                val1 = float(values[0])
                val2 = float(values[1])
              except:
                self.raiseAnError(IOError,' Wrong R0values associated to ETanalysis Post-Processor')
              self.variables[variableID]['R0low']  = min(val1,val2)
              self.variables[variableID]['R0high'] = max(val1,val2)
            else:
              self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                ' : attribute node R0 missing')
            if 'simVarID' in child.attrib.keys():
              self.variables[variableID]['simVarID'] = child.attrib['simVarID']
              self.dynamicVariablesList.append(child.attrib['simVarID'])
            else:
              self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                ' : attribute node simVarID missing')
        elif child.tag == 'mode':
            self.mode = child.text
            allowedModes = ['classification','ETrecalc']
            if self.mode not in allowedModes:
                self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                  ' : attribute node value for XML node: ' + str(child) + ' not allowed (classification or ETrecalc)')
        elif child.tag == 'target':
            self.target['targetID'] = child.text
            if 'R1values' in child.attrib.keys():
              values = child.attrib['R1values'].split(',')
              if len(values) != 2:
                self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                  ' : attribute node values for XML node: ' + str(child) + ' has one or more than two values')
              try:
                val1 = float(values[0])
                val2 = float(values[1])
              except:
                self.raiseAnError(IOError,' Wrong target values associated to ETanalysis Post-Processor')
              self.target['low']  = min(val1,val2)
              self.target['high'] = max(val1,val2)
            else:
              self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                ' : attribute node values is not present for XML node: ' + str(child) )
        elif child.tag == 'branchID':
            self.branchID = child.text
        elif child.tag !='method':
            self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                       ' : XML node ' + str(child) + ' is not recognized')

  def run(self,inputDic):
      if len(inputDic) == 2:
          for inp in inputDic:
            if set(self.ETvariablesList) == set(inp['data']['input'].keys()):
                self.ETdataset = copy.deepcopy(inp)
            if set(self.dynamicVariablesList).issubset(set(inp['data']['input'].keys())):
                self.dynamicDataset = copy.deepcopy(inp)
          self.expandedETdata()
          if self.mode == 'classification':
              outDic = self.runClassification()
          elif self.mode == 'ETrecalc':
              outDic = self.runETrecalc()
      else:
          self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor requires two data sets in input')

  def expandedETdata(self):
      print(self.ETdataset['data'])
      for key in self.ETdataset['data']['input'].keys():
          minus1indexes = np.where(np.asarray(self.ETdataset['data']['input'][key])==-1)
          print(key,minus1indexes)
          if any(map(len, minus1indexes)):
              for index in minus1indexes[0]:
                  print(index)
                  for keyUpdate in self.ETdataset['data']['input'].keys():
                      if key == keyUpdate:
                        self.ETdataset['data']['input'][key][index] = 0
                        self.ETdataset['data']['input'][key] = np.append(self.ETdataset['data']['input'][key],1)
                      else:
                        self.ETdataset['data']['input'][keyUpdate] = np.append(self.ETdataset['data']['input'][keyUpdate],self.ETdataset['data']['input'][keyUpdate][index])
                  for keyUpdate in self.ETdataset['data']['output'].keys():
                      self.ETdataset['data']['output'][keyUpdate] = np.append(self.ETdataset['data']['output'][keyUpdate],self.ETdataset['data']['output'][keyUpdate][index])
      print(self.ETdataset['data'])

  def runETrecalc(self):
    inputWeights = self.dynamicDataset['metadata']['ProbabilityWeight']
    pb_branch = np.zeros(self.ETdataset[self.ETvariablesList[0]].size)

    self.adaptedData={}

    for var in self.variables.keys():
        self.adaptedData[var] = (self.variables[var][low] <= self.dynamicDataset['data']['input'][var] <= self.variables[var][high]).astype(int)

    indexes=np.range(inputWeights.size)
    for i in range(self.branches.size):
        for var in self.variables:
            tempIndexes = np.where(self.adaptedData[var]==self.branches[i][var])
            indexes = np.intersect1d(indexes,tempIndexes)
        pb_branch[i] = np.sum(inputWeights[indexes])

    return inp

  def runClassification(self,inputDic):
    noBranches = self.ETdataset['data']['input'][self.ETvariablesList[0]].size
    noSimulations = self.dynamicDataset['data']['input'][self.dynamicVariablesList[0]].size
    self.labels = np.zeros(self.dynamicDataset[self.dynamicVariablesList[0]].size)

    for var in self.variables.keys():
        self.adaptedData[var] = (self.variables[var][low] <= self.dynamicDataset['data']['input'][var] <= self.variables[var][high]).astype(int)

    index = np.arange(noBranches)
    #for i in range(noBranches):
