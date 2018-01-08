'''Module for loading and parsing configuration files'''

from ciscoconfparse import CiscoConfParse


class ConfigFile(object):
  '''
  Represents a configuration file to be loaded and parsed.
  '''
  def __init__(self, file_name=None):
    '''
    :file_name: string name of a configuration file to load
    '''
    self.contents = ''
    if file_name is not None:
      self.load(file_name)

  def load(self, file_name):
    '''
    Loads a configuration file

    :file_name: string name of a configuration file to load
    '''
    with open(file_name) as file_stream:
      contents = ''.join(file_stream.readlines())
    self.contents = contents

  def from_string(self, config_string):
    '''
    Loads a configuration file from a string

    :config_string: string with configuration text
    '''
    self.contents = config_string
    return self



class CiscoConfig(ConfigFile):
  '''
  Represents a Cisco configuration from a switch.
  '''
  @property
  def parse(self):
    '''
    Returns CiscoConfParse object from loaded configuration.
    '''
    contents = self.contents
    if isinstance(contents, str):
      contents = contents.split('\n')
    return CiscoConfParse(contents)
