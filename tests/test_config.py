"""
Test VirtstrapConfig
====================
"""
from virtstrap.config import VirtstrapConfig, ConfigurationError
from nose.tools import *

FAKE_CONFIG = """
list_section:
  - value1
  - value2
  - value3

kv_section:
  key1: value1

---
profile: profile1

list_section:
  - value4

kv_section:
  key2: value2

---
profile: profile2

list_section:
  - value5

kv_section:
  key1: override1
"""

BAD_CONFIG = """
list_section:
  - value1

---
profile: profile1

list_section:
  - value4

---
profile: profile1

list_section:
  - value5
"""
def create_fake_config():
    return VirtstrapConfig.from_string(FAKE_CONFIG)

def test_load_config_from_string():
    """Test that we can load a config at all"""
    config = create_fake_config()
    assert isinstance(config, VirtstrapConfig)

@raises(ConfigurationError)
def test_load_config_from_bad_string():
    """Test loading of a bad configuration"""
    config = VirtstrapConfig.from_string(BAD_CONFIG)

class TestVirtstrapConfig(object):
    def setup(self):
        self.config = create_fake_config()

    def test_config_collect_default_list_section(self):
        """Collect the default list section from config string"""
        section_data = self.config.section("list_section")
        assert section_data == ["value1", "value2", "value3"]

    def test_config_collect_mulitple_list_sections(self):
        section_data1 = self.config.section("list_section", 
                profiles=["profile1"])
        section_data2 = self.config.section("list_section", 
                profiles=["profile2"])
        assert section_data1 == ["value1", "value2", "value3", "value4"]
        assert section_data2 == ["value1", "value2", "value3", "value5"]





