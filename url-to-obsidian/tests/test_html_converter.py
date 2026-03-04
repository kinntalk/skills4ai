import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from html_converter import clean_html, html_to_markdown

class TestHtmlConverter(unittest.TestCase):
    def test_clean_html_default(self):
        html = "<div><script>alert('xss')</script><p>Content</p></div>"
        cleaned = clean_html(html)
        self.assertNotIn("script", cleaned)
        self.assertIn("Content", cleaned)
        
    def test_clean_html_custom(self):
        html = "<div class='ad'>Ad Content</div><p>Real Content</p>"
        cleaned = clean_html(html, remove_selectors=[".ad"])
        self.assertNotIn("Ad Content", cleaned)
        self.assertIn("Real Content", cleaned)
        
    def test_html_to_markdown(self):
        html = "<h1>Title</h1><p>Paragraph</p>"
        md = html_to_markdown(html)
        self.assertIn("# Title", md)
        self.assertIn("Paragraph", md)

if __name__ == "__main__":
    unittest.main()
