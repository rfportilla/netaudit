'''Unit tests for config'''

import unittest
from mock import patch, mock_open

from ciscoconfparse import CiscoConfParse

#from . import common
import tests.common as C
#from netaudit.config import ConfigFile, CiscoConfig
from netaudit import config


class ConfigFileTests(unittest.TestCase):
  '''
  Tests for config files
  '''
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_from_string_sets_contents(self):
    myconf = config.ConfigFile().from_string(C.SAMPLE_CONFIG)
    self.assertEquals(myconf.contents, C.SAMPLE_CONFIG)

  @patch.object(config.ConfigFile, 'load')
  def test_init_file_name_calls_load(self, mock_config_file_load):
    file_name = 'someFile'
    config.ConfigFile(file_name)
    mock_config_file_load.called_once_with(file_name)

  @patch('netaudit.config.open', new_callable=mock_open(
    read_data=C.SAMPLE_CONFIG), create=True)
  def test_load_opens_file_specified(self, mock_config_file_open):
    file_name = 'someFile'
    config.ConfigFile(file_name)
    mock_config_file_open.assert_called_with(file_name)

  @patch('netaudit.config.open', new=mock_open(
    read_data=C.SAMPLE_CONFIG), create=True)
  def test_load_sets_contents(self):
    file_name = 'someFile'
    config_file = config.ConfigFile(file_name)
    self.assertEquals(config_file.contents, C.SAMPLE_CONFIG)



class CiscoConfigTests(unittest.TestCase):
  '''
  Tests for Config
  '''
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_is_config_file(self):
    cisco_config = config.CiscoConfig()
    self.assertIsInstance(cisco_config, config.ConfigFile)

  def test_parse_returns_ciscoconfparse(self):
    cisco_config = config.CiscoConfig()
    cisco_config.from_string(C.SAMPLE_CONFIG)
    self.assertIsInstance(cisco_config.parse, CiscoConfParse)



if __name__ == '__main__':
  unittest.main()
