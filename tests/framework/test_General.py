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
  This Module performs Unit Tests for the randomUtils methods
"""

#For future compatibility with Python 3
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)

import os
import sys
import pytest
import numpy as np
frameworkDir = os.path.abspath(os.path.join(os.path.dirname(__file__),*(['..']*2 + ['framework'])))
sys.path.append(frameworkDir)

from RavenTests import FrameworkTest


class TestGeneralFramework(FrameworkTest):
  def test_ExternalModel(self):
    tests = {'externalModel/testPrintHistorySet_dump.csv':None}
    testDir = os.getcwd()
    self.runRavenTest('test_Lorentz.xml',tests,testDir)

  """
    <TestInfo>
      <name>framework.randomUtils</name>
      <author>talbpaul</author>
      <created>2017-06-16</created>
      <classesTested>utils.randomUtils</classesTested>
      <description>
         This test performs Unit Tests for the randomUtils methods
      </description>
      <revisions>
        <revision author="talbpaul" date="2018-06-14">Moved from python script to pytest format</revision>
      </revision>
    </TestInfo>
  """
