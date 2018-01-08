'''Test from file'''

from netaudit.audit import AuditTests, TestFile
from netaudit.config import ConfigFile

def basic_line_matching():
  ''' Test config file using basic line matching'''
  #Load configuration file to test
  conf = ConfigFile('config.txt')
  #Load test definition file
  tests = TestFile()
  tests.load('tests.yaml')
  #Sets version to test for
  tests.config_version = 'Catalyst3750'
  
  #create test suite from auditor and run tests
  suite = AuditTests(config=conf, tests=tests, test_group='Basic')
  suite.run()
  #Display results
  for test in suite.last_results:
      result = 'OK' if test.result else 'FAIL'
      print('%s: %s' % (test.name, result))

def hierarchical_line_matching():
  ''' Test config file using hierarchical matching '''
  #Load configuration file to test
  conf = ConfigFile('config.txt')
  #Load test definition file
  tests = TestFile()
  tests.load('tests.yaml')
  #Sets version to test for
  tests.config_version = 'Catalyst3750'

  #create test suite from auditor and run tests
  suite = AuditTests(config=conf, tests=tests, test_group='Advanced')
  suite.run()
  #Display results
  for test in suite.last_results:
      result = 'OK' if test.result else 'FAIL'
      print('%s: %s' % (test.name, result))


if __name__ == '__main__':
  print "Basic Tests:"
  basic_line_matching()
  
  print "\nAdvanced Tests:"
  hierarchical_line_matching()
