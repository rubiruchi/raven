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

class locaAnalysis(PostProcessorInterfaceBase):
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
    pass

  def run(self,inputDic):
    """
     This method perform the actual calculation of the risk measures
     @ In, inputDic, list, list of dictionaries which contains the data inside the input DataObjects
     @ Out, outputDic, dict, dictionary which contains the risk measures
    """
    inp = inputDic[0]
    inputWeights = inp['metadata']['ProbabilityWeight']
    pb_branch = np.zeros(4)
    inp['data']['output']['label']=np.zeros(inputWeights.size)
    inp['data']['output']['probability']=np.zeros(inputWeights.size)

    for i in range(inputWeights.size):
        inp['data']['output']['probability'][i]=inputWeights[i]
        if inp['data']['input']['ACC1'][i]==0.0 or inp['data']['input']['ACC2'][i]==0.0:
            if inp['data']['input']['LPI_A_FS'][i]==0.2 or inp['data']['input']['LPI_B_FS'][i]==0.2:
                if inp['data']['input']['LPR_A_FS'][i]==120.0 or inp['data']['input']['LPR_B_FS'][i]==120.0:
                    pb_branch[0] += inputWeights[i]
                    inp['data']['output']['label'][i]=1
                else:
                    pb_branch[1] += inputWeights[i]
                    inp['data']['output']['label'][i]=2
            else:
                pb_branch[2] += inputWeights[i]
                inp['data']['output']['label'][i]=3
        else:
            pb_branch[3] += inputWeights[i]
            inp['data']['output']['label'][i]=4

    print(pb_branch)

    return inp
