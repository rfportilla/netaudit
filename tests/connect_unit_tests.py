'''Unit tests for connect'''

import unittest
from mock import patch, MagicMock

import paramiko

from netaudit import connect
import telnetlib


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

  def test_init_sets_optional_properties(self):
    opts = {'username': {'prop': 'username', 'value': 'myName'},
            'password': {'prop': 'password', 'value': 'myPass'},
            'port': {'prop': 'port', 'value': 2702},
            'ssh_option': {'prop': 'ssh_opts', 'value': 'ExtraOption'}}
    for opt in opts:
      cfg = connect.Connection(hostname=self.hostname, **{opt:
                                                          opts[opt]['value']})
      prop_value = opts[opt]['value']
      if opt == 'ssh_option':
        prop_value = {'ssh_option': opts['ssh_option']['value']}
      self.assertEqual(getattr(cfg, opts[opt]['prop']), prop_value)

  def test_init_sets_required_properties(self):
    opts = {'hostname': {'prop': 'hostname', 'value': 'myHost'}}
    kwargs = {x: opts[x]['value'] for x in opts}
    cfg = connect.Connection(**kwargs)
    for opt in opts:
      self.assertEqual(getattr(cfg, opts[opt]['prop']), opts[opt]['value'])

  def test_set_properties(self):
    opts = {'hostname': {'prop': 'hostname', 'value': 'otherHost'},
            'username': {'prop': 'username', 'value': 'myName'},
            'password': {'prop': 'password', 'value': 'myPass'},
            'port': {'prop': 'port', 'value': 2702},
            'ssh_opts': {'prop': 'ssh_opts', 'value': {'a': 'apple'}}}
    for opt in opts:
      cfg=connect.Connection(hostname=self.hostname)
      setattr(cfg, opt, opts[opt]['value'])
      self.assertEqual(getattr(cfg, opt), opts[opt]['value'])




class SSHClientTests(unittest.TestCase):
  '''
  Tests for SSH Client
  '''
  def setUp(self):
    opts = {'hostname': 'myhost', 'username': 'jsmith', 'password': 'secret'}
    self.connection = connect.Connection(**opts)
    patchers = {
      'SSHClient': patch('paramiko.SSHClient', spec=True),
#      'Channel': patch('paramiko.Channel', spec=True),
#      'Transport': patch('paramiko.Transport', spec=True),
      }
    mocks = {
      'SSHClient': patchers['SSHClient'].start(),
#      'Channel': patchers['Channel'].start(),
#      'Transport': patchers['Transport'].start(),
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

  def test_init_sets_optional_properties(self):
    opts = {'max_sess_tries': {'prop': 'MAX_SESS_TRIES', 'value': 20},
            'cmd_timeout': {'prop': 'CMD_TIMEOUT', 'value': 15},
            'open_sess_timeout': {'prop': 'OPEN_SESS_TIMEOUT', 'value': 27},
            'ssh_eol': {'prop': 'SSH_EOL', 'value': '\r\n'},
            'max_buffer_length': {'prop': 'MAX_BUFFER_LENGTH', 'value': 9876},
            'max_buffer_cycle': {'prop': 'MAX_BUFFER_CYCLE', 'value': 17},
            'default_port': {'prop': 'DEFAULT_PORT', 'value': '1722'}}
    for opt in opts:
      client = connect.SSH_Client(self.connection, **{opt: opts[opt]['value']})
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  def test_init_sets_required_properties(self):
    opts = {'connection': {'prop': 'connection', 'value': self.connection}}
    kwargs = {x: opts[x]['value'] for x in opts}
    client = connect.SSH_Client(**kwargs)
    for opt in opts:
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  def test_set_properties(self):
    otherConnection = connect.Connection(hostname='defaultHN')
    opts = {'connection': {'prop': 'connection', 'value': otherConnection},
            'max_sess_tries': {'prop': 'MAX_SESS_TRIES', 'value': 20},
            'cmd_timeout': {'prop': 'CMD_TIMEOUT', 'value': 15},
            'open_sess_timeout': {'prop': 'OPEN_SESS_TIMEOUT', 'value': 27},
            'ssh_eol': {'prop': 'SSH_EOL', 'value': '\r\n'},
            'max_buffer_length': {'prop': 'MAX_BUFFER_LENGTH', 'value': 9876},
            'max_buffer_cycle': {'prop': 'MAX_BUFFER_CYCLE', 'value': 17},
            'default_port': {'prop': 'DEFAULT_PORT', 'value': 1722},
            'channel': {'prop': 'channel', 'value': 'whatever'}}
    for opt in opts:
      client = connect.SSH_Client(self.connection)
      setattr(client, opts[opt]['prop'], opts[opt]['value'])
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  def test_send_command_calls_chan_send(self):
    command = 'show me the money\n'
    client = connect.SSH_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.channel.send.assert_called_once_with(command)

  def test_connect_calls_ssh_connect(self):
    client = connect.SSH_Client(self.connection, cmd_timeout=0)
    client.connect()
    self.mocks['SSHClient']().connect.assert_called()

  def test_channel_error_raises(self):
    client = connect.SSH_Client(self.connection, cmd_timeout=0)
    def raise_side_effect():
      raise EOFError
    self.mocks['SSHClient']().get_transport.side_effect = raise_side_effect
    self.assertRaises(EOFError, getattr, client, 'channel')

  def test_send_command_adds_eol(self):
    command = 'show me the money'
    client = connect.SSH_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.channel.send.assert_called_once_with(command + client.SSH_EOL)



class TelnetClientTests(unittest.TestCase):
  '''
  Tests for Telnet Client
  '''
  def setUp(self):
    opts = {'hostname': 'myhost', 'username': 'jsmith', 'password': 'secret'}
    self.connection = connect.Connection(**opts)
    patchers = {
    #  'Telnet': patch('telnetlib.Telnet', spec=True),
      }
    mocks = {
    #  'Telnet': patchers['Telnet'].start(),
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

  def test_init_sets_optional_properties(self):
    opts = {'max_sess_tries': {'prop': 'MAX_SESS_TRIES', 'value': 20},
            'cmd_timeout': {'prop': 'CMD_TIMEOUT', 'value': 15},
            'open_sess_timeout': {'prop': 'OPEN_SESS_TIMEOUT', 'value': 27},
            'telnet_eol': {'prop': 'TELNET_EOL', 'value': '\r\n'},
            'max_buffer_length': {'prop': 'MAX_BUFFER_LENGTH', 'value': 9876},
            'max_buffer_cycle': {'prop': 'MAX_BUFFER_CYCLE', 'value': 17},
            'default_port': {'prop': 'DEFAULT_PORT', 'value': '1722'}}
    for opt in opts:
      client = connect.Telnet_Client(self.connection, **{opt: opts[opt]['value']})
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  def test_init_sets_required_properties(self):
    opts = {'connection': {'prop': 'connection', 'value': self.connection}}
    kwargs = {x: opts[x]['value'] for x in opts}
    client = connect.Telnet_Client(**kwargs)
    for opt in opts:
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  def test_set_properties(self):
    otherConnection = connect.Connection(hostname='defaultHN')
    opts = {'connection': {'prop': 'connection', 'value': otherConnection},
            'max_sess_tries': {'prop': 'MAX_SESS_TRIES', 'value': 20},
            'cmd_timeout': {'prop': 'CMD_TIMEOUT', 'value': 15},
            'open_sess_timeout': {'prop': 'OPEN_SESS_TIMEOUT', 'value': 27},
            'telnet_eol': {'prop': 'TELNET_EOL', 'value': '\r\n'},
            'max_buffer_length': {'prop': 'MAX_BUFFER_LENGTH', 'value': 9876},
            'max_buffer_cycle': {'prop': 'MAX_BUFFER_CYCLE', 'value': 17},
            'default_port': {'prop': 'DEFAULT_PORT', 'value': 1722}}
    for opt in opts:
      client = connect.Telnet_Client(self.connection)
      setattr(client, opts[opt]['prop'], opts[opt]['value'])
      self.assertEqual(getattr(client, opts[opt]['prop']), opts[opt]['value'])

  @patch.object(telnetlib.Telnet, 'read_very_eager')
  @patch.object(telnetlib.Telnet, 'open')
  def test_connect_calls_telnet_connect(self, mock_telnet, mock_tn_read):
    client = connect.Telnet_Client(self.connection, cmd_timeout=0)
    client.client = telnetlib.Telnet()
    client.connect()
    mock_telnet.assert_called()

  @patch('telnetlib.Telnet')
  def test_send_command_calls_client_write(self, mock_telnet):
    command = 'show me the money\n'
    client = connect.Telnet_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.client.write.assert_called_once_with(command)

  @patch('telnetlib.Telnet')
  def test_send_command_adds_eol(self, mock_telnet):
    command = 'show me the money'
    client = connect.Telnet_Client(self.connection, cmd_timeout=0)
    client.send_command(command)
    client.client.write.assert_called_once_with(command + client.TELNET_EOL)



if __name__ == '__main__':
  unittest.main('__main__')#, 'ConnectionTests.test_init_sets_required_properties')
