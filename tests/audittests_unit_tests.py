''''Unit tests for audit'''

import unittest
from mock import patch, mock_open, PropertyMock, MagicMock
import mock

#from . import common
import tests.common as C
from netaudit import exceptions as E
from netaudit import audit
from netaudit.config import ConfigFile

class TestFileTests(unittest.TestCase):
  '''
  Tests for TestFile
  '''
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_fromString_sets_test_groups(self):
    expected = C.SAMPLE_TEST_FILE_DICT
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertEquals(test_file.test_groups, expected['TestGroups'])

  def test_from_string_sets_test_defintions(self):
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertGreater(len(test_file.test_definitions), 0)

  def test_test_files_sets_default_first(self):
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertEquals('Default', test_file.test_definitions[0][0])

  @patch('yaml.safe_load', new=MagicMock())
  @patch('netaudit.audit.open', new_callable=mock_open(
    read_data=C.SAMPLE_TEST_FILE), create=True)
  def test_load_calls_open(self, mock_file_stream):
    filename = 'someFile'
    audit.TestFile().load(filename)
    mock_file_stream.assert_called_with(filename)

  @patch('netaudit.audit.open', new=mock_open(
    read_data=C.SAMPLE_TEST_FILE), create=True)
  def test_load_sets_test_groups(self):
    filename = 'someFile'
    mytest = audit.TestFile()
    mytest.load(filename)
    expected = C.SAMPLE_TEST_FILE_DICT
    self.assertDictEqual(mytest.test_groups, expected['TestGroups'])

  @patch.object(audit.TestFile, 'load')
  def test_init_fileName_calls_load(self, mock_test_file_load):
    filename = 'someFile'
    audit.TestFile(filename)
    mock_test_file_load.assert_called_once_with(filename)

  @patch('netaudit.audit.open', new=mock_open(
    read_data=C.SAMPLE_TEST_FILE), create=True)
  def test_load_sets_test_files(self):
    filename = 'someFile'
    test_file = audit.TestFile()
    test_file.load(filename)
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertGreater(len(test_file.test_definitions), 0)

  def test_config_version_raiseserror_if_not_str(self):
    test_file = audit.TestFile()
    self.assertRaises(ValueError, setattr, test_file, 'config_version', 2)

  def test_config_version_sets_str(self):
    version = 'MyVersion'
    test_file = audit.TestFile()
    test_file.config_version = version
    self.assertEquals(test_file.config_version, version)

  def test_find_test_by_name_gets_testcase_object(self):
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    mytest = test_file.find_test_by_name('test2')
    self.assertIsInstance(mytest, audit.TestCase)

  def test_find_test_by_name_gets_default_test(self):
    test_name = 'test2'
    expected = 'this_is_test2_Default'
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertEquals(test_file.find_test_by_name(test_name).pattern, expected)

  def test_find_test_by_name_gets_child_test(self):
    test_name = 'bin-test'
    expected = 'this_is_cat3750'
    test_file = audit.TestFile()
    test_file.config_version = 'Catalyst3750'
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertEquals(test_file.find_test_by_name(test_name).pattern, expected)

  def test_find_test_by_name_not_found_raises(self):
    test_name = 'NotFound'
    test_file = audit.TestFile()
    test_file.from_string(C.SAMPLE_TEST_FILE)
    self.assertRaises(E.TestNotFoundError, test_file.find_test_by_name,
                      test_name)



class TestCaseTests(unittest.TestCase):
  '''
  Tests for TestCase
  '''
  def setUp(self):
    self.properties = {
      'name': 'MyTest',
      'command': 'MyCommand',
      'pattern': 'Pattern(Match)',
      'expected': 'Match',
      'type': 'Text'
    }

  def tearDown(self):
    self.properties = None

  def test_init_properties_set(self):
    properties = self.properties
    case = audit.TestCase(properties['name'], properties['command'],
                          properties['pattern'], properties['expected'],
                          properties['type'])
    for attr in properties:
      self.assertEqual(getattr(case, attr), properties[attr])

  def test_properties_setter(self):
    properties = self.properties
    case = audit.TestCase(properties['name'])
    for attr in properties:
      if attr == 'name':
        continue
      setattr(case, attr, properties[attr])
      self.assertEqual(getattr(case, attr), properties[attr])

  def test_getresult_result_returns_true(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value='PatternMatch')
    properties = self.properties
    case = audit.TestCase(properties['name'], pattern=properties['pattern'],
                          expected=properties['expected'])
    result = case.get_result(conf)
    self.assertTrue(result)

  def test_getresult_result_returns_false(self):
    conf = MagicMock(ConfigFile)
    conf.contents = PropertyMock()
    properties = self.properties
    case = audit.TestCase(properties['name'], pattern=properties['pattern'],
                          expected=properties['expected'])
    result = case.get_result(conf)
    self.assertFalse(result)

  def test_getresult_config_result_returns_true(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/28', '(shutdown)']
    expected = 'shutdown'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    self.assertTrue(case.get_result(conf))

  def test_getresult_config_result_returns_false(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/27', '(shutdown)']
    expected = 'shutdown'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    self.assertFalse(case.get_result(conf))

  def test_getresult_deep_config_result_returns_false(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/1$', 'Child Configuration',
               'Grandchild (Configuration)']
    expected = 'noMatch'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    self.assertFalse(case.get_result(conf))

  def test_getresult_deep_config_result_returns_true(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/1$', 'Child Configuration',
               'Grandchild (Configuration)']
    expected = 'Configuration'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    self.assertTrue(case.get_result(conf))

  def test_getresult_deep_config_intermediate_returns_false(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/1$', 'Childish Configuration',
               'Grandchild (Configuration)']
    expected = 'Configuration'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    self.assertFalse(case.get_result(conf))

  def test_getresult_deep_config_result_sets_message(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/1$', 'Child Configuration',
               'Grandchild (Configuration)']
    expected = 'noMatch'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    case.get_result(conf)
    self.assertRegexpMatches(case.last_message, '^Match failed')

  def test_getresult_deep_config_intermediate_sets_message(self):
    conf = MagicMock(ConfigFile)
    type(conf).contents = PropertyMock(return_value=C.SAMPLE_CONFIG)
    pattern = ['interface GigabitEthernet1/0/1$', 'Childish Configuration',
               'Grandchild (Configuration)']
    expected = 'Configuration'
    case = audit.TestCase('testTest', pattern=pattern, expected=expected)
    case.get_result(conf)
    self.assertRegexpMatches(case.last_message, '^Could not find child')




class AuditTestsTests(unittest.TestCase):
  '''
  Tests for audit test
  '''
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_init_sets_configfile(self):
    my_config = C.FakeConfigFile()
    suite = audit.AuditTests(my_config)
    self.assertIs(suite.config, my_config)

  def test_init_sets_tests(self):
    my_tests = audit.TestFile()
    suite = audit.AuditTests(C.FakeConfigFile(), my_tests)
    self.assertIs(suite.tests, my_tests)

  def test_init_sets_test_group(self):
    my_testgroup = 'group_to_test'
    suite = audit.AuditTests(C.FakeConfigFile(), audit.TestFile(),
                             my_testgroup)
    self.assertIs(suite.test_group, my_testgroup)

  def test_init_named_attribute_sets_tests(self):
    my_tests = audit.TestFile()
    suite = audit.AuditTests(C.FakeConfigFile(), tests=my_tests)
    self.assertIs(suite.tests, my_tests)

  def test_init_named_attribute_sets_test_group(self):
    my_testgroup = 'group_to_test'
    suite = audit.AuditTests(C.FakeConfigFile(), test_group=my_testgroup)
    self.assertIs(suite.test_group, my_testgroup)

  def test_tests_property_sets_tests(self):
    my_tests = audit.TestFile()
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.tests = my_tests
    self.assertIs(suite.tests, my_tests)

  def test_test_group_property_sets_test_group(self):
    my_testgroup = 'group_to_test'
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.test_group = my_testgroup
    self.assertIs(suite.test_group, my_testgroup)



class AuditTestsRunTests(unittest.TestCase):
  '''
  Tests for audit test run method
  '''
  def setUp(self):
    patchers = {
      'TestCase': patch('netaudit.audit.TestCase', spec=True),
      'TestFile': patch('netaudit.audit.TestFile', spec=True)
      }
    mocks = {
      'TestCase': patchers['TestCase'].start(),
      'TestFile': patchers['TestFile'].start(),
      }
    self.patchers = patchers
    self.mocks = mocks
    for patcher in self.patchers.itervalues():
      self.addCleanup(patcher.stop)

    self.mocks['TestCase']().get_result.return_value = True

    self.mocks['TestFile']().find_test_by_name.return_value = audit.TestCase()
    type(mocks['TestFile']()).test_groups = PropertyMock(
      return_value={'testGroup1': ['test1']})

  def tearDown(self):
    del self.patchers
    del self.mocks

  def test_run_calls_testfile_find_test_by_name(self):
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.tests = audit.TestFile('fake_file')
    suite.test_group = 'testGroup1'
    suite.run()
    suite.tests.find_test_by_name.assert_called_once_with('test1')

  def test_run_calls_testcase_getresult(self):
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.tests = audit.TestFile('fake_file')
    suite.test_group = 'testGroup1'
    suite.run()
    audit.TestCase().get_result.assert_called_once_with(suite.config)

  def test_run_unset_test_group_raises_error(self):
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.tests = audit.TestFile('fake_file')
    self.assertRaises(E.TestGroupNotSetError, suite.run)

  def test_run_test_group_not_found_raises_error(self):
    suite = audit.AuditTests(C.FakeConfigFile())
    suite.tests = audit.TestFile('fake_file')
    suite.test_group = 'testGroup2'
    self.assertRaises(E.TestGroupDoesNotExistError, suite.run)




if __name__ == '__main__':
  unittest.main()
