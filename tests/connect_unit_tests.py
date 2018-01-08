'''Unit tests for connect'''

import unittest
from mock import patch, mock_open

import paramiko

from netaudit import connect


class ConnectionTests(unittest.TestCase):
  '''
  Tests for connection class
  '''
  def setUp(self):
    self.hostname = 'myHost'
    self.username = 'jsmith'
    self.password = 'secret'

  def tearDown(self):
    for attr in ['hostname', 'username', 'password']:
      delattr(self, attr)

  def test_init_requires_hostname(self):
    self.assertRaises(TypeError, connect.Connection)

  def test_init_sets_hostname(self):
    cfg = connect.Connection(hostname=self.hostname)
    self.assertEqual(cfg.hostname, self.hostname)

  def test_init_sets_username(self):
    cfg = connect.Connection(hostname=self.hostname, username=self.username)
    self.assertEqual(cfg.username, self.username)

  def test_init_sets_password(self):
    cfg = connect.Connection(hostname=self.hostname, password=self.password)
    self.assertEqual(cfg.password, self.password)

  def test_set_hostname_property(self):
    new_hostname = 'otherHost'
    cfg = connect.Connection(hostname=self.hostname)
    cfg.hostname = new_hostname
    self.assertEqual(cfg.hostname, new_hostname)

  def test_set_username_property(self):
    cfg = connect.Connection(hostname=self.hostname)
    cfg.username = self.username
    self.assertEqual(cfg.username, self.username)

  def test_set_password_property(self):
    cfg = connect.Connection(hostname=self.hostname)
    cfg.password = self.password
    self.assertEqual(cfg.password, self.password)



class SSHClientTests(unittest.TestCase):
  '''
  Tests for SSH Client
  '''
  def setUp(self):
    opts = {'hostname': 'myhost', 'username': 'jsmith', 'password': 'secret'}
    self.connection = connect.Connection(**opts)
    patchers = {
      'SSHClient': patch('paramiko.SSHClient', spec=True),
      'Channel': patch('paramiko.Channel', spec=True),
      'Transport': patch('paramiko.Transport', spec=True),
      }
    mocks = {
      'SSHClient': patchers['SSHClient'].start(),
      'Channel': patchers['Channel'].start(),
      'Transport': patchers['Transport'].start(),
      }
    self.patchers = patchers
    self.mocks = mocks
    for patcher in self.patchers.itervalues():
      self.addCleanup(patcher.stop)

  def tearDown(self):
    for attr in ['connection', 'patchers', 'mocks']:
      delattr(self, attr)

  def test_init_requires_connection(self):
    self.assertRaises(TypeError, connect.SSH_Client)

  def test_send_command_calls_chan_send(self):
    command = 'show me the money\n'
    client = connect.SSH_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.channel.send.assert_called_once_with(command)



class TelnetClientTests(unittest.TestCase):
  '''
  Tests for Telnet Client
  '''
  def setUp(self):
    opts = {'hostname': 'myhost', 'username': 'jsmith', 'password': 'secret'}
    self.connection = connect.Connection(**opts)
    patchers = {
      'Telnet': patch('telnetlib.Telnet', spec=True),
      }
    mocks = {
      'Telnet': patchers['Telnet'].start(),
      }
    self.patchers = patchers
    self.mocks = mocks
    for patcher in self.patchers.itervalues():
      self.addCleanup(patcher.stop)

  def tearDown(self):
    for attr in ['connection', 'patchers', 'mocks']:
      delattr(self, attr)

  def test_init_requires_connection(self):
    self.assertRaises(TypeError, connect.Telnet_Client)

  def test_send_command_calls_client_write(self):
    command = 'show me the money\n'
    client = connect.Telnet_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.client.write.assert_called_once_with(command)



if __name__ == '__main__':
  unittest.main()
