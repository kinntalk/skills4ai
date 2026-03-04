import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

if __name__ == "__main__":
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    
    if not result.wasSuccessful():
        sys.exit(1)
