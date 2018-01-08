import netaudit.audit
import netaudit.config
import netaudit.tests

confFile = '/repos/netaudit/sample/catalyst3750_1.txt'
testTemplate = '/repos/netaudit/configs/tests.yaml'

conf = netaudit.config.ConfigFile(confFile)
tests = netaudit.tests.TestFile()
tests.load(testTemplate)
testName = 'Basic'

auditor = netaudit.audit.AuditTests(config=conf, tests=tests,
                                    testGroup=testName)
auditor.run()
print(auditor.lastResults[0].result)

for test in auditor.lastResults:
    print('Test: %s  Result: %s' % (test.name, test.result))
