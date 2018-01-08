'''Common components for unit tests'''
import yaml

SAMPLE_TEST_FILE = '''---

TestItems:
  Default:
    bin-test:
      cmd: ""
      match: "this_is_Default"
      expected: ""
    test2:
      cmd: ""
      match: "this_is_test2_Default"
      expected: "match2"
  'Catalyst3750':
    bin-test:
      cmd: ""
      match: "this_is_cat3750"
      expected: ""

TestGroups:
  Basic:
    - bin-test
'''

SAMPLE_TEST_FILE_DICT = yaml.safe_load(SAMPLE_TEST_FILE)

SAMPLE_CONFIG = '''!
version 12.2
no service pad
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname SampleSwitch
!
boot-start-marker
boot-end-marker
!
enable secret 5 $2$YUkWa$Me.ImInAFortuneCooky/
enable password pass123
!
username admin password 0 pass123
!
!
no aaa new-model
switch 1 provision ws-c3750g-24ts
system mtu routing 1500
authentication mac-move permit
ip subnet-zero
ip domain-name fake.dom
!
!
!
!
!
!
!
!
spanning-tree mode pvst
spanning-tree etherchannel guard misconfig
spanning-tree extend system-id
!
vlan internal allocation policy ascending
!
ip ssh version 2
!
!
interface GigabitEthernet1/0/1
  Child Configuration
    Grandchild Configuration
!
interface GigabitEthernet1/0/2
!         
interface GigabitEthernet1/0/3
!
interface GigabitEthernet1/0/4
!
interface GigabitEthernet1/0/5
!
interface GigabitEthernet1/0/6
!
interface GigabitEthernet1/0/7
!
interface GigabitEthernet1/0/8
!
interface GigabitEthernet1/0/9
!
interface GigabitEthernet1/0/10
!
interface GigabitEthernet1/0/11
!
interface GigabitEthernet1/0/12
!
interface GigabitEthernet1/0/13
!
interface GigabitEthernet1/0/14
!
interface GigabitEthernet1/0/15
!
interface GigabitEthernet1/0/16
!
interface GigabitEthernet1/0/17
!
interface GigabitEthernet1/0/18
!
interface GigabitEthernet1/0/19
!
interface GigabitEthernet1/0/20
!
interface GigabitEthernet1/0/21
!
interface GigabitEthernet1/0/22
!
interface GigabitEthernet1/0/23
!
interface GigabitEthernet1/0/24
!
interface GigabitEthernet1/0/25
!         
interface GigabitEthernet1/0/26
!
interface GigabitEthernet1/0/27
!
interface GigabitEthernet1/0/28
 description noaccess
 shutdown
!
interface Vlan1
 ip address 192.168.0.3 255.255.255.0
!
ip classless
ip http server
ip http secure-server
!
ip sla enable reaction-alerts
snmp-server community public RO
!
!
line con 0
line vty 0 4
 password pass123
 login local
 transport input ssh
line vty 5 15
 password pass123
 login
!
end

'''

class FakeConfigFile(object):
  '''Fake for ConfigFile class'''
  pass

class FakeTestFile(object):
  '''Fake for TestFile class'''
  tests = SAMPLE_TEST_FILE_DICT
  test_groups = {'testGroup1': ['test1', 'test2'],
                 'testGroup2': ['test2', 'test3']}
