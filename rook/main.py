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
This module is the main program for running tests.
"""
from __future__ import division, print_function, absolute_import
import warnings

import os
import sys
import argparse
import re
import inspect
import time
import threading

import psutil
import pool
import trees.TreeStructure
from Tester import Tester, Differ

warnings.simplefilter('default', DeprecationWarning)

parser = argparse.ArgumentParser(description="Test Runner")
parser.add_argument('-j', '--jobs', dest='number_jobs', type=int, default=1,
                    help='Specifies number of tests to run simultaneously (default: 1)')
parser.add_argument('--re', dest='test_re_raw', default='.*',
                    help='Only tests with this regular expression inside will be run')
parser.add_argument('-l', dest='load_average', type=float, default=-1.0,
                    help='wait until load average is below the number before starting a new test')
parser.add_argument('--heavy', action='store_true',
                    help='Run only heavy tests')

parser.add_argument('--list-testers', action='store_true', dest='list_testers',
                    help='Print out the possible testers')

args = parser.parse_args()

class LoadClass(threading.Thread):
  """
    This class keeps track of the one second load average
  """

  def __init__(self):
    """
      Initialize this class
      @ In, None
      @ Out, None
    """
    threading.Thread.__init__(self)
    self.__load_avg = psutil.cpu_percent(1.0)*psutil.cpu_count()/100.0
    self.__load_lock = threading.Lock()
    self.daemon = True #Exit even if this thread is running.

  def run(self):
    """
      Run forever, grabbing the load average every second
      @ In, None
      @ Out, None
    """
    while True:
      load_avg = psutil.cpu_percent(1.0)*psutil.cpu_count()/100.0
      with self.__load_lock:
        self.__load_avg = load_avg

  def get_load_average(self):
    """
      Get the most recent load average
      @ In, None,
      @ Out, float value for load average (average number of processors running)
    """
    load_avg = -1
    with self.__load_lock:
      load_avg = self.__load_avg
    return load_avg

if args.load_average > 0:
  load = LoadClass()
  load.start()

def load_average_adapter(function):
  """
    Adapts function to not start until load average is low enough
    @ In, function, function, function to call
    @ Out, new_func, function, function that checks load average before running
  """
  def new_func(data):
    """
      function that waits until load average is lower.
      @ In, data, Any, data to pass to function
      @ Out, result, result of running function on data
    """
    #basically get the load average for 0.1 seconds:
    while load.get_load_average() > args.load_average:
      time.sleep(1.0)
    return function(data)
  return new_func

def get_test_lists(directory):
  """
    Returns a list of all the files named tests under the directory
    @ In, directory, string, the directory to start at
    @ Out, dir_test_list, list, the files named tests
  """
  dir_test_list = []
  for root, _, files in os.walk(directory):
    if 'tests' in files:
      dir_test_list.append((root, os.path.join(root, 'tests')))
  return dir_test_list

def get_testers_and_differs(directory):
  """
    imports all the testers and differs in a directory
    @ In, directory, string, directory to search
    @ Out, (tester_dict, differ_dict), tuple of dictionaries
      returns dictionaries with all the subclasses of Tester and Differ.
  """
  tester_dict = {}
  differ_dict = {}
  os.sys.path.append(directory)
  for filename in os.listdir(directory):
    if filename.endswith(".py") and not filename.startswith("__"):
      module = __import__(filename[:-3]) #[:-3] to remove .py
      for name, value in module.__dict__.items():
        #print("Unknown", name, value)
        if inspect.isclass(value) and value is not Tester\
           and issubclass(value, Tester):
          tester_dict[name] = value
        if inspect.isclass(value) and value is not Differ\
           and issubclass(value, Differ):
          differ_dict[name] = value

  return tester_dict, differ_dict

def sec_format(runtime):
  """
    Formats the runtime into a string of the number seconds.
    If runtime is none, format as None!
    @ In, runtime, float or None, runtime to be formated.
    @ Out, sec_format, string of runtime.
  """
  if isinstance(runtime, float):
    return "{:6.2f}sec".format(runtime)
  return "  None!  "

def process_result(index, _input_data, output_data):
  """
    This is a callback function that Processes the result of a test.
    @ In, index, int, Index into functions list.
    @ In, _input_data, ignored, the input data passed to the function
    @ In, output_data, Tester.TestResult the output data passed to the function
    @ Out, None
  """
  group = output_data.group
  process_test_name = test_name_list[index]
  if group == Tester.group_success:
    results["pass"] += 1
    for postreq in function_postreq.get(process_test_name, []):
      if postreq in name_to_id:
        job_id = name_to_id[postreq]
        print("Enabling", postreq, job_id)
        run_pool.enable_job(job_id)
  elif group == Tester.group_skip:
    results["skipped"] += 1
    print(output_data.message)
  else:
    results["fail"] += 1
    failed_list.append(process_test_name)
    print(output_data.output)
    print(output_data.message)
  number_done = sum(results.values())
  print("({}/{}) {:7s} ({}) {}".format(number_done, len(function_list),
                                       Tester.get_group_name(group),
                                       sec_format(output_data.runtime),
                                       process_test_name))
if __name__ == "__main__":

  test_re = re.compile(args.test_re_raw)

  #XXX fixme to find a better way to the tests directory

  this_dir = os.path.abspath(os.path.dirname(__file__))
  up_one_dir = os.path.dirname(this_dir)
  base_test_dir = os.path.join(up_one_dir, "tests")


  test_list = get_test_lists(base_test_dir)

  base_testers, base_differs = get_testers_and_differs(this_dir)
  testers, differs = get_testers_and_differs(os.path.join(up_one_dir, "scripts",
                                                          "TestHarness", "testers"))
  testers.update(base_testers)
  differs.update(base_differs)

  if args.list_testers:
    print("Testers:")
    for tester_name, tester in testers.items():
      print("Tester:", tester_name)
      print(tester.get_valid_params())
      print()
    print("Differs:")
    for differ_name, differ in differs.items():
      print("Differ:", differ_name)
      print(differ.get_valid_params())
      print()

  tester_params = {}
  for tester in testers:
    tester_params[tester] = testers[tester].get_valid_params()

  function_list = [] #Store the data for the pool runner
  test_name_list = []
  ready_to_run = []
  function_postreq = {} #If this is non-empty for a key, enable the postreq's
  name_to_id = {}

  for test_dir, test_file in test_list:
    #print(test_file)
    tree = trees.TreeStructure.getpot_to_input_node(open(test_file, 'r'))
    for node in tree:
      #print(node.tag)
      #print(node.attrib)
      param_handler = tester_params[node.attrib['type']]
      if not param_handler.check_for_required(node.attrib):
        print("Missing Parameters in:", node.tag)
      if not param_handler.check_for_all_known(node.attrib):
        print("Unknown Parameters in:", node.tag, test_file)
      rel_test_dir = test_dir[len(base_test_dir)+1:]
      test_name = rel_test_dir+os.sep+node.tag
      if "prereq" in node.attrib:
        prereq = node.attrib['prereq']
        prereq_name = rel_test_dir+os.sep+prereq
        l = function_postreq.get(prereq_name, [])
        l.append(test_name)
        function_postreq[prereq_name] = l
        has_prereq = True
      else:
        has_prereq = False
      if test_re.search(test_name):
        params = dict(node.attrib)
        params['test_dir'] = test_dir
        tester = testers[node.attrib['type']](test_name, params)
        if args.heavy:
          tester.run_heavy()
        for child in node.children:
          #print(test_name,"child",child)
          child_type = child.attrib['type']
          child_param_handler = differs[child_type].get_valid_params()
          if not child_param_handler.check_for_required(child.attrib):
            print("Missing Parameters in:", child.tag, node.tag, test_file)
          if not child_param_handler.check_for_all_known(child.attrib):
            print("Unknown Parameters in:", child.tag, node.tag, test_file)
          differ = differs[child_type](child.tag, dict(child.attrib), test_dir)
          tester.add_differ(differ)
        id_num = len(function_list)
        #input_filename = node.attrib['input']
        func = tester.run
        if args.load_average > 0:
          func = load_average_adapter(func)
        function_list.append((func, (test_dir)))
        test_name_list.append(test_name)
        ready_to_run.append(not has_prereq)
        name_to_id[test_name] = id_num

  run_pool = pool.MultiRun(function_list, args.number_jobs, ready_to_run)

  run_pool.run()

  results = {"pass":0, "fail":0, "skipped":0}
  failed_list = []

  output_list = run_pool.process_results(process_result)
  run_pool.wait()

  if results["fail"] > 0:
    print("FAILED:")
  for path in failed_list:
    print(path)

  csv_report = open("test_report.csv", "w")
  csv_report.write(",".join(["name", "passed", "group", "time"])+"\n")
  for result, test_name in zip(output_list, test_name_list):
    if result is not None:
      group_name = Tester.get_group_name(result.group)
      out_line = ",".join([test_name, str(result.group == Tester.group_success),
                           group_name, str(result.runtime)])
    else:
      out_line = ",".join([test_name, str(False), "NO_PREREQ", str(0.0)])
    csv_report.write(out_line+"\n")
  csv_report.close()

  print("PASSED:", results["pass"], "FAILED:", results["fail"], "SKIPPED", results["skipped"])
  sys.exit(results["fail"])
