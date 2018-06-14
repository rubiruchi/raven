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
  This Module sets up common utilities for RAVEN tests
"""

#For future compatibility with Python 3
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)

import os
import sys
import pytest
import numpy as np
import pandas as pd
pd.set_option('max_seq_items',7)

# framework
frameworkDir = os.path.join(os.path.dirname(__file__),'..','..','framework')
sys.path.append(frameworkDir)
# math utils
from utils import mathUtils


class FrameworkTest(object):
  def runRavenTest(self,fname,tests,testDir,ordered=True,relErr=1e-10):
    """
      Runs traditional framework tests.
      @ In, fname, str, name of input to run (xml file)
      @ In, tests, dict, keys are test files and gold are files to check against
      @ In, testDir, str, directory of test file
    """
    self.__rel_err = relErr # TODO is this threadsafe? Also need to use it.
    raven = os.path.join(os.path.dirname(__file__),'..','..','raven_framework')
    command = raven + ' ' + os.path.abspath(fname) + ' > '+fname+'.log' # TODO better log capturing?
    os.system(command)
    # TODO multiple test types, this is specifically for CSV
    for test,gold in tests.items():
      if gold is None:
        gold = os.path.join('gold',test)
      test = os.path.join(testDir,test)
      gold = os.path.join(testDir,gold)
      self._checkCSV(test,gold,ordered=ordered)

  #################
  #     Files     #
  #################
  def checkFiles(self,*files):
    """
      Checks that all given files exist.
      @ In, files, list, list of files to check
      @ Out, None
    """
    for f in files:
      assert os.path.isfile(f)

  #################
  #      CSV      #
  #################
  def _checkCSV(self,testFile,goldFile,ordered=True):
    """
      Compares two CSVs for testing
      @ In, testFile, string, absolute path of test file
      @ In, goldFile, string, absolute path of gold file
      @ In, ordered, bool, optional, if False then rows OR columns could be swapped (but contents consistent)
      @ Out, None
    """
    self.checkFiles(testFile,goldFile)
    test = self._csvLoad(testFile)
    gold = self._csvLoad(goldFile)
    # if gold is empty (None) then test has to be too, and vice versa
    if gold is None:
      assert test is None, 'Gold "{}" is empty, but test "{}" is not!'.format(goldFile,testFile)
      # if they're both None, then no more checking to do
      return
    else:
      assert test is not None, 'Gold "{}" is not empty, but test "{}" is!'.format(goldFile,testFile)
    if ordered:
      # while this works for ordered, it does not for unordered (as we want it)
      ## while it has the check_like option, that searches within each column for matches,
      ## and doesn't require one whole row to be consistent.
      #assert gold.equals(test)
      pd.testing.assert_frame_equal(test,gold,
                                    check_less_precise=8,   # TODO fix for tol as input
                                    obj='CSV')
    else:
      # compare content and shape
      ## compare column headers
      diffColumns = set(gold.columns)^set(test.columns)
      assert len(diffColumns) == 0, 'Columns have mismatched headers: "{}"'.format(', '.join(diffColumns))
      ## check number of entries
      assert len(gold.index) == len(test.index), 'Different number of rows: gold "{}" versus test "{}"' \
                                                 .format(len(gold.index),len(test.index))
      # now CSVs are same shape and size and headers, so diff CSVs
      ## align columns
      test = test[gold.columns.tolist()]
      ## scrub CSV for marginal values, and mark infinites
      test = self._csvScrub(test)
      gold = self._csvScrub(gold)
      ## check for matching rows
      for idx in gold.index:
        find = gold.iloc[idx].rename(None)
        match = self._csvFindRow(find,test)
        # TODO what if there are multiple matches?
        # TODO remove match from test (maybe if it's singular)?
        assert len(match), 'No match in test "{}" for gold row "{}"!'.format(idx+1,find)

  def _csvFindRow(self,row,csv):
    """
      searches for a match of "row" in "csv"
      @ In, row, pd.Series, row of data
      @ In, csv, pd.Dataframe, dataframe to look in
      @ Out, match, pd.Dataframe, matching row of data (or empty list if not found)
    """
    match = csv.copy()
    # TODO binomial search?
    # TODO remove match whenever it is found so searching speeds up
    ## TODO transfer comments from UnorderedCSVDiff in TestHarness/testers
    for idx,val in row.iteritems():
      match = match.sort_values(idx)
      matchVal = match[idx].values.item(0) if match[idx].values.shape[0] != 0 else None
      matchIsNumber = mathUtils.isAFloatOrInt(matchVal)
      valIsNumber = mathUtils.isAFloatOrInt(val)
      if matchIsNumber != valIsNumber:
        # columns don't have matching data!
        return []
      if matchIsNumber:
        sign = np.sign(val)
        lowest = np.searchsorted(match[idx].values,val*(1.0-sign*self.__rel_err))
        highest = np.searchsorted(match[idx].values,val*(1.0+sign*self.__rel_err),side='right')-1
      else:
        lowest = np.searchsorted(match[idx].values,val)
        highest = np.searchsorted(match[idx].values,val,side='right')-1
      if lowest == len(match[idx]):
        return []
      condition = match[idx].values[lowest] == pytest.approx(val,self.__rel_err) if matchIsNumber else \
                  match[idx].values[lowest] == val
      if not condition:
        return []
      match = match[slice(lowest,highest+1)]
    return match

  def _csvLoad(self,filename):
    """
      Loads CSVs into pandas DataFrame objects.
      @ In, filename, str, absolute path to file to load
      @ Out, csv, pandas.DataFrame, csv as dataframe
    """
    try:
      csv = pd.read_csv(filename,sep=',')
    # if file is empty, store as None
    except pd.errors.EmptyDataError:
      csv = None
    except Exception:
      pytest.fail('CSV "{}" failed to load!')
    return csv

  def _csvScrub(self,csv,tol=1e-10): # TODO zero threshold instead of 1e-10
    """
      Cleans up CSV dataframe for easy comparison, by:
       - For any columns that contain numbers, set near-zero values to zero
       - Replace infs and nans with symbolic values
      @ In TODO
    """
    # TODO absolute value check
    csv = csv.replace(np.inf,-sys.maxint)
    csv = csv.replace(np.nan, sys.maxint)
    for col in csv.columns:
      example = csv[col].values.item(0) if csv[col].values.shape[0] != 0 else None
      # if a number, flatten toward zero
      if mathUtils.isAFloatOrInt(example):
        csv[col].values[np.isclose(csv[col].values,0,rtol=tol)] = 0
    return csv

