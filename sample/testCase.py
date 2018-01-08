import netaudit.audit
import netaudit.config

confFile = '/media/sf_repos/netaudit/sample/catalyst3750_1.txt'
testTemplate = '/media/sf_repos/netaudit/sample/tests.yaml'

conf = netaudit.config.ConfigFile(confFile)
tests = netaudit.audit.TestFile()
tests.load(testTemplate)
tests.config_version = ['Cisco', 'Catalyst3750']
testName = 'Basic'

auditor = netaudit.audit.AuditTests(config=conf, tests=tests,
                                    test_group=testName)
auditor.run()
print(auditor.last_results[0].result)

for test in auditor.last_results:
    print('Test: %s  Result: %s' % (test.name, test.result))
