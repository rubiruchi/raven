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
frameworkDir = os.path.abspath(os.path.join(os.path.dirname(__file__),*(['..']*4 + ['framework'])))
sys.path.append(frameworkDir)
from utils import utils
utils.find_crow(frameworkDir)
from utils import randomUtils
randomENG = utils.findCrowModule("randomENG")
randomUtils.stochasticEnv = 'crow'

@pytest.fixture
def seed():
  randomUtils.randomSeed(42)


class TestRandomUtils(object):
  def test_random(self):
    assert randomUtils.random() == pytest.approx(0.8147237)

  def test_randomSeed(self,seed):
    assert randomUtils.random() == pytest.approx(0.37454011)
    # if seed change didn't change seed, next would be 0.9507 ish
    randomUtils.randomSeed(12345)
    assert randomUtils.random() == pytest.approx(0.92961609)

  def test_vector_single(self,seed):
    # single sampling
    vals = np.array([randomUtils.random() for _ in range(int(1e5))])
    mean = np.average(vals)
    stdv = np.std(vals)
    assert mean == pytest.approx(0.5,2e-3)
    assert stdv == pytest.approx(np.sqrt(1./12.),2e-3)

  def test_vector_batch_1d(self,seed):
    # 1d batch sampling
    vals = randomUtils.random(1e5)
    mean = np.average(vals)
    stdv = np.std(vals)
    assert mean == pytest.approx(0.5,2e-3)
    assert stdv == pytest.approx(np.sqrt(1./12.),2e-3)

  def test_vector_batch_2d(self,seed):
    vals = randomUtils.random(10,1000)
    mean = np.average(vals)
    stdv = np.std(vals)
    assert mean == pytest.approx(0.5,2e-3)
    assert stdv == pytest.approx(np.sqrt(1./12.),2e-3)

  def test_normal(self,seed):
    # test box-muller
    mean,stdev = randomUtils.BoxMullerGenerator().testSampling(1e5)
    assert mean == pytest.approx(0, abs=5e-3)
    assert stdev == pytest.approx(1.0, 1.1e-3)
    # test single value
    assert randomUtils.randomNormal() == pytest.approx(-0.13233865)
    # test single point
    right = [-0.56039014,  0.47329822,  1.08827208]
    vals = randomUtils.randomNormal(3)
    assert vals == pytest.approx(right)
    # test SHAPE of a few points
    vals = randomUtils.randomNormal(3,5)
    assert len(vals) == 5
    assert len(vals[0]) == 3
    assert vals.shape == (5,3)

  def test_integers(self,seed):
    right = [14,18,20,12,17]
    n = [randomUtils.randomIntegers(10,20,None) for _ in range(len(right))]
    #for i in range(len(right)):
    #  n = randomUtils.randomIntegers(10,20,None) # no need for a message handler, for now
    assert n == right

  def test_permutations(self,seed):
    l = [1,2,3,4,5]
    l2 = randomUtils.randomPermutation(l,None)
    assert l2 == [2,4,5,1,3]

  def test_hypersphere_surface(self,seed):
    # just check the points are on the unit hypersphere, no need to check values
    for N in range(1,6):
      pt = randomUtils.randPointsOnHypersphere(N)
      assert np.sum(pt*pt) == pytest.approx(1.0)

  def test_hypersphere_surface_radius(self,seed):
    # check sum of squares is square of radius (pythagorus)
    for r in [0.2,0.7,1.5,10.0, 100.0]:
      pt = randomUtils.randPointsOnHypersphere(4,r=r)
      assert np.sum(pt*pt) == pytest.approx(r*r)

  def test_hypersphere_surface_multisample(self,seed):
    # just test shapes, radius
    samps = randomUtils.randPointsOnHypersphere(5,samples=100)
    assert samps.shape == (100,5)
    for s in samps:
      assert np.sum(s*s) == pytest.approx(1.0)

  def visualize_hypersphere_surface(self,seed):
    # NOT a test, but helps with visually checking points
    import matplotlib.pyplot as plt
    samps = randomUtils.randPointsOnHypersphere(2,samples=1e4)
    x = samps[:,0]
    y = samps[:,1]
    plt.plot(x,y,'.')
    plt.show()

  def test_hypersphere_interior(self,seed):
    for i in range(1,6):
      pt = randomUtils.randPointsInHypersphere(i)
      assert np.sum(pt*pt) <= 1.0

  def test_hypersphere_interior_radius(self,seed):
    for r in [0.2,0.7,1.5,10.0, 100.0]:
      pt = randomUtils.randPointsInHypersphere(4,r=r)
      assert np.sum(pt*pt) <= r*r

  def test_hypersphere_interior_multisample(self,seed):
    # just test shapes, radius
    samps = randomUtils.randPointsInHypersphere(5,samples=100)
    assert samps.shape == (100,5)
    for s in samps:
      assert np.sum(s*s) <= 1.0

  def test_RNG_instance(self):
    # more tests Crow engine than this module
    first = randomENG.RandomClass()
    second = randomENG.RandomClass()
    # check same
    assert first.random() == pytest.approx(second.random())
    # check different when seeded
    first.seed(200286)
    second.seed(20021986)
    assert not (first.random() == pytest.approx(second.random()))
    # same when seeded again
    first.seed(200286)
    second.seed(200286)
    assert first.random() == pytest.approx(second.random())

  def test_RNG_factory(self):
    first = randomUtils.newRNG()
    second = randomUtils.newRNG()
    # check same
    assert first.random() == pytest.approx(second.random())
    # check different when seeded
    first.seed(200286)
    second.seed(20021986)
    assert not (first.random() == pytest.approx(second.random()))
    # same when seeded again
    first.seed(200286)
    second.seed(200286)
    assert first.random() == pytest.approx(second.random())

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
