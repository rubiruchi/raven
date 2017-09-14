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

    for child in xmlNode:
        if child.tag == 'variable':
        variableID = child.text
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
        elif child.tag == 'target':
            self.target['targetID'] = child.text
            if 'values' in child.attrib.keys():
              values = child.attrib['values'].split(',')
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
        elif child.tag !='method':
            self.raiseAnError(IOError, 'ETanalysis Interfaced Post-Processor ' + str(self.name) +
                                       ' : XML node ' + str(child) + ' is not recognized')

  def run(self,inputDic):
    """
     This method perform the actual calculation of the risk measures
     @ In, inputDic, list, list of dictionaries which contains the data inside the input DataObjects
     @ Out, outputDic, dict, dictionary which contains the risk measures
    """
    inp = inputDic[0]
    inputWeights = inp['metadata']['ProbabilityWeight']
    pb_branch = np.zeros(self.branches.size)

    self.adaptedData={}

    for var in self.variables:
        self.adaptedData[var] = (self.variables[var][low] <= inp['data']['input'][var] <= self.variables[var][high]).astype(int)

    indexes=np.range(inputWeights.size)
    for i in range(self.branches.size):
        for var in self.variables:
            tempIndexes = np.where(self.adaptedData[var]==self.branches[i][var])
            indexes = np.intersect1d(indexes,tempIndexes)
        pb_branch[i] = np.sum(inputWeights[indexes])

    return inp
