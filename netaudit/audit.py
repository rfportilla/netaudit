'''Module for auditing a configuration file'''

import re
import collections

import yaml
from ciscoconfparse import CiscoConfParse

from . import exceptions as E

DEFAULT_CONF = 'Default'

class AuditTests(object):
  '''
  Auditor that can accept a set of tests and configuration file and then
  returns results.
  '''
  def __init__(self, config, tests=None, test_group=None):
    '''
    :config: netaudit.ConfigFile object
    :tests: tests.TestFile object
    :test_group: String, test group name
    '''
    self.config = config
    self.tests = tests
    self.test_group = test_group
    self.last_results = None

  def run(self, test_group=None):
    '''
    Runs tests in a given test_group and sets self.last_results to a list of
    the results

    :test_group: string name of group to run
    '''
    results = []
    self.test_group = self.test_group if test_group is None else test_group
    test_group = self.test_group
    if test_group is None:
      msg = 'test_group must be set before running audit.'
      raise E.TestGroupNotSetError(msg)
    if test_group not in self.tests.test_groups:
      msg = ('The specified test group (%s) does not exist in the '
             'configuration file.' % test_group)
      raise E.TestGroupDoesNotExistError(msg)
    for test_name in self.tests.test_groups[test_group]:
      test = self.tests.find_test_by_name(test_name)
      result = test.get_result(self.config)
      message = None if test.last_message is None else test.last_message
      #result = self._getTestResult(self.config, test)
      results.append(TestResult(test_name, result, message))
    self.last_results = results



class TestFile(object):
  '''
  Used to load and parse a test definition file written in YAML.  Look in
  sample/tests.yaml for example of configuration.
  '''
  test_definitions = []
  test_groups = {}

  def __init__(self, file_name=None):
    '''
    :file_name: string name of file to load
    '''
    self.test_definitions = list(self.test_definitions)
    self.test_groups = dict(self.test_groups)
    self._config_version = []
    if file_name is not None:
      self.load(file_name)

  def load(self, file_name):
    '''
    Loads test definitions from file.

    :file_name: string name of file
    '''
    with open(file_name) as file_stream:
      yaml_conf = yaml.safe_load(file_stream)
    self._parse_conf(yaml_conf)

  def from_string(self, test_definition_string):
    '''
    Loads test definitions from string

    :test_definition_string: string with test definitions
    '''
    self._parse_conf(yaml.safe_load(test_definition_string))

  def _parse_conf(self, yaml_conf):
    '''
    Parses configuration from yaml and populates self.test_groups and
    self.test_definitions

    :yaml_conf: yaml object
    '''
    for item in yaml_conf['TestItems']:
      add_item = [item, yaml_conf['TestItems'][item]]
      # Default should be the first in the list
      if item == 'Default':
        self.test_definitions = [add_item] + self.test_definitions
      else:
        self.test_definitions.append(add_item)
    if 'TestGroups' in yaml_conf:
      for group in yaml_conf['TestGroups']:
        self.test_groups[group] = yaml_conf['TestGroups'][group]

  @property
  def config_version(self):
    '''Returns specified configuration version'''
    return self._config_version

  @config_version.setter
  def config_version(self, version):
    '''
    Sets configuration version

    :version: string version text'''
    if isinstance(version, str):
      self._config_version = [version]
    elif isinstance(version, collections.Iterable):
      self._config_version = tuple(version)
    else:
      msg = ('"%s" is not a valid string or list.  Set config_version to a '
             'string or list of strings.' % str(version))
      raise ValueError(msg)

  def find_test_by_name(self, test_name):
    '''
    Returns TestCase object  based config_version and test_name.  If test is
    not defined for the specific config_version (or config_version is not
    specified), the test in Default is used.

    :test_name: string test name as defined in test definition file
    '''
    test = None
    test_definitions = self.test_definitions

    
    for config_version in reversed([DEFAULT_CONF] + list(self.config_version)):
      test_definition_match = None
      for test_definition in test_definitions:
        if test_definition[0] == config_version:
          test_definition_match = test_definition
      if test_definition_match is None:
        msg = ('Make sure the test item exists and has the specified '
           'test (%s).' % (config_version))
        raise E.TestItemNotFoundError(msg)
      if test_name in test_definition_match[1]:
        test = test_definition_match[1][test_name]
        return TestCase(
          test_name=test_name,
          command=test['cmd'] if 'cmd' in test else None,
          pattern=test['match'],
          expected=test['expected'],
          test_type=test['type'] if 'type' in test else None,
        )
    msg = ('Make sure the test configuration exists and has the specified '
           'test (%s).' % (test_name))
    raise E.TestNotFoundError(msg)



TestResult = collections.namedtuple('TestResult', ('name', 'result',
                                                   'message'))



class TestCase(object):
  '''
  Represents a single test that can be run and returns a TestResult object.
  '''
  def __init__(self, test_name, command=None, pattern=None, expected=None,
               test_type='text'):
    '''
    :test_name: The name of the test to be run.
    :command: The command that must be run to get the raw data
    :pattern: Regex pattern to find configuration item
    :expected: Expected value to match pattern
    :test_type: Type of test defines how test is completed; 'text' does
      simple text search through the entire configuration; 'config' first
      parses the text as a hierarchy (tree structure)
    '''
    self.name = test_name
    self.command = command
    self.pattern = pattern
    self.expected = expected
    self.type = test_type
    self._last_message = None

  def get_result(self, config):
    '''
    Returns a boolean result after running the defined test on the passed
    configuration

    :configuration: a configuration object as defined in netaudit.config
    '''
    contents = config.contents
    result = False
    message = ''
    if self.type == 'config' or isinstance(self.pattern, list):
      has_failure = False# Track if there is an explicit failure
      parse = CiscoConfParse(re.split('(?:\r\n|\n|\r)',contents))
      patterns = self.pattern

      parents = parse.find_objects(patterns[0])
      for i in range(1, len(patterns)):
        children = []
        for parent in parents:
          if i >= len(patterns) - 1:
            match = parent.re_match_iter_typed(patterns[i], default=None)
            if match and match == self.expected:
              result = True
            else:
              has_failure = True
              message += ("Match failed for configuration, line %r.\n" %
                               (parent.linenum))
          else:
            match = parent.re_search_children(patterns[i])
            if match:
              children.extend(match)
            else:
              has_failure = True
              message += ("Could not find child, line %r.\n" %
                               (parent.linenum))
        parents = children
      result = (not has_failure) & result
    elif self.type == 'text' or self.type is None:
      for line in contents.split('\n'):
        #print ('%s, %s, %s' % (test.pattern, test.expected, line))
        match = re.search(self.pattern, line)
        if match is not None and match.group(1) == self.expected:
          result = True
    self._last_message = message if message != '' else None
    return result

  @property
  def last_message(self):
    return self._last_message
