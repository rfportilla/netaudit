'''Module for connecting to a switch and pulling a configuration'''

import re

import paramiko
import telnetlib
from time import sleep


class Connection(object):
  '''Connection class to hold settings'''

  __slots__ = ['hostname', 'username', 'password', 'port', 'ssh_opts']

  def __init__(self, hostname, port=None, username=None, password=None,
               retries=3, **kwargs):
    '''
    :hostname: Required String, name or IP of host to connect to
    :username: String, username for authentication
    :password: String, password for authentication
    '''
    self.hostname = hostname
    self.username = username
    self.password = password
    self.port = port
    self.ssh_opts = kwargs



class SSH_Client(object):
  '''SSH Client'''

  __slots__ = ['connection', '_ssh_channel', 'MAX_SESS_TRIES', 'CMD_TIMEOUT',
               'OPEN_SESS_TIMEOUT', 'SSH_EOL', 'MAX_BUFFER_LENGTH',
               'MAX_BUFFER_CYCLE', 'DEFAULT_PORT', '_last_response', '_client']

  def __init__(self, connection, max_sess_tries=3, cmd_timeout=3,
               open_sess_timeout=5, ssh_eol='\n', max_buffer_length=9999,
               max_buffer_cycle=10, default_port=22):
    '''
    :max_sess_tries: Integer, number of times to try connecting to SSH host
    :cmd_timeout: Integer, number of seconds to allow a command to run
    :open_sess_timeout: Integer, number of seconds to allow SSH session to
      start.  This occurs after the connection is made.
    :ssh_eol: String, End of line character(s)
    :max_buffer_length: Integer, number of characters to pull from buffer.
      Default value is good to start with.  This works with max_buffer_cycle.
    :max_buffer_cycle: number of times to try to get data before deciding it is
      too large.  Each getting of data is of size max_buffer_length.
    :default_port: Integer, port number to connect to on remote host.
    '''
    self.connection = connection
    self._ssh_channel = None
    self.MAX_SESS_TRIES = max_sess_tries
    self.CMD_TIMEOUT = cmd_timeout
    self.OPEN_SESS_TIMEOUT = open_sess_timeout
    self.SSH_EOL = ssh_eol
    self.MAX_BUFFER_LENGTH = max_buffer_length
    self.MAX_BUFFER_CYCLE = max_buffer_cycle
    self.DEFAULT_PORT = default_port
    self._last_response = None


  @property
  def client(self):
    '''
    Provides paramiko SSH client.
    '''
    try:
      self._client.get_transport().send_ignore()
    except (EOFError, AttributeError):
      ssh = paramiko.SSHClient(**self.connection.ssh_opts)
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(
        self.connection.hostname,
        username=self.connection.username,
        password=self.connection.password,
      )
      self._client = ssh
    return self._client

  @client.setter
  def client(self, client):
    self._client = client

  def connect(self):
    '''
    Attempts to connect ssh client.
    '''
    self.client
    sleep(self.CMD_TIMEOUT)
    self._last_response = self._read()
    return self.last_response

  @property
  def channel(self):
    if self._ssh_channel is None:
      self.client = None
      for i in range(self.MAX_SESS_TRIES):
        try:
          t = self.client.get_transport()
          self._ssh_channel = t.open_session(timeout=self.OPEN_SESS_TIMEOUT)
          self._ssh_channel.invoke_shell()
        except (EOFError, paramiko.ssh_exception.SSHException):
          if i == self.MAX_SESS_TRIES - 1:
            raise
          continue
        break
    return self._ssh_channel

  @channel.setter
  def channel(self, channel):
    self._ssh_channel = channel

  def _read(self):
    chan = self.channel
    response, err_response = '', ''
    for i in range(self.MAX_BUFFER_CYCLE):
      if chan.recv_ready():
        response += chan.recv(self.MAX_BUFFER_LENGTH)
      if chan.recv_stderr_ready():
        err_response += chan.recv_stderr(self.MAX_BUFFER_LENGTH)
    return (response, err_response)

  def send_command(self, command, timeout=None):
    '''
    Send command to remote host.

    :command: String command to send
    :timeout: Number of seconds to wait for command result
    '''
    chan = self.channel
    timeout = timeout if timeout is not None else self.CMD_TIMEOUT
    chan.settimeout(timeout)
    if not re.search(r'%s$' % self.SSH_EOL, command):
      command += self.SSH_EOL
    if chan.send_ready():
      chan.send(command)
      sleep(self.CMD_TIMEOUT)
    self._last_response = self._read()
    return self.last_response

  @property
  def last_response(self):
    return self._last_response



class Telnet_Client(object):
  '''Telnet Client'''

  __slots__ = ['connection', 'MAX_SESS_TRIES', 'CMD_TIMEOUT',
               'OPEN_SESS_TIMEOUT', 'TELNET_EOL', 'MAX_BUFFER_LENGTH',
               'MAX_BUFFER_CYCLE', 'DEFAULT_PORT', '_last_response', '_client']

  def __init__(self, connection, max_sess_tries=3, cmd_timeout=3,
               open_sess_timeout=5, telnet_eol='\n', max_buffer_length=9999,
               max_buffer_cycle=10, default_port=23):
    '''
    :max_sess_tries: Integer, number of times to try connecting to Telnet host
    :cmd_timeout: Integer, number of seconds to allow a command to run
    :open_sess_timeout: Integer, number of seconds to allow Telnet session to
      start. This occurs after the connection is made.
    :telnet_eol: String, End of line character(s)
    :max_buffer_length: Integer, number of characters to pull from buffer.
      Default value is good to start with.  This works with max_buffer_cycle.
    :max_buffer_cycle: number of times to try to get data before deciding it is
      too large.  Each getting of data is of size max_buffer_length.
    :default_port: Integer, port number to connect to on remote host.
    '''
    self.connection = connection
    self.MAX_SESS_TRIES = max_sess_tries
    self.CMD_TIMEOUT = cmd_timeout
    self.OPEN_SESS_TIMEOUT = open_sess_timeout
    self.TELNET_EOL = telnet_eol
    self.MAX_BUFFER_LENGTH = max_buffer_length
    self.MAX_BUFFER_CYCLE = max_buffer_cycle
    self.DEFAULT_PORT = default_port
    self._last_response = None

  def connect(self):
    '''
    Connect to Telnet host and return banner and beginning text.
    '''
    self.client
    sleep(self.CMD_TIMEOUT)
    self._last_response = (self.client.read_very_eager(),'')
    return self.last_response

  @property
  def client(self):
    '''
    Provides telnetlib Telnet client.
    '''
    try:
      self._client.sock.sendall(telnetlib.IAC + telnetlib.NOP)
    except (EOFError, AttributeError):
      conf = self.connection
      port = conf.port if conf.port is not None else self.DEFAULT_PORT
      self._client = telnetlib.Telnet(conf.hostname, port,
                                      self.OPEN_SESS_TIMEOUT)
    return self._client

  @client.setter
  def client(self, client):
    '''
    Set client property.  Typically used to reset the client by setting to
    None.

    :client: client object.
    '''
    self._client = client

  def send_command(self, command, timeout=None):
    '''
    Send command to Telnet host.

    :command: command text to send.  If EOL not found, it is appended.
    :timeout: time to wait for response from command.
    '''
    response, err_response = '', ''
    timeout = timeout if timeout is not None else self.CMD_TIMEOUT
    if not re.search(r'%s$' % self.TELNET_EOL, command):
      command += self.TELNET_EOL
    self.client.write(command)
    sleep(self.CMD_TIMEOUT)
    response += self.client.read_very_eager()
    self._last_response = (response, err_response)
    return self.last_response

  @property
  def last_response(self):
    '''
    Contains last response received from telnet host.
    '''
    return self._last_response


'''
if __name__ == '__main__':
  ctelnet = False
  if ctelnet == True:
    conf = Connection('192.168.0.221', username='admin', password='l3tm3in')
    client = Telnet_Client(conf, telnet_eol='\n')
    print 'connect: ___\n%s\n___' % client.connect()[0]
    if re.search('Password: ', client.last_response[0]):
      print client.send_command(conf.password)
    client.send_command('term len 0')
    res = client.send_command('sh ver', 1)
    print 'result:\n%s\n\nstderr:\n%s\n\n' % (res[0], res[1])
  else:
    conf = Connection('192.168.0.221', username='admin', password='l3tm3in')
    client = SSH_Client(conf)
    print 'connect: ___\n%s\n___' % client.connect()[0]
    client.send_command('term len 0')
    res = client.send_command('sh ver', 1)
    print 'result:\n%s\n\nstderr:\n%s\n\n' % (res[0], res[1])
#'''
