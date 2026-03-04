import unittest
import shutil
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_config_dir")
        self.config_manager = ConfigManager(self.test_dir)
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            
    def test_default_config(self):
        config = self.config_manager.load()
        self.assertIn("browser", config)
        self.assertIn("content_extraction", config)
        self.assertIn("remove_selectors", config["content_extraction"])
        
    def test_set_get(self):
        self.config_manager.set("browser.timeout", 5000)
        self.assertEqual(self.config_manager.get("browser.timeout"), 5000)
        
    def test_credentials(self):
        domain = "example.com"
        user = "testuser"
        password = "testpassword"
        
        self.config_manager.set_credentials(domain, user, password)
        creds = self.config_manager.get_credentials(domain)
        
        self.assertEqual(creds["username"], user)
        self.assertEqual(creds["password"], password)

if __name__ == "__main__":
    unittest.main()
