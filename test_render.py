import unittest
import mdviewer


class RenderTests(unittest.TestCase):
    def test_tables_and_code(self):
        page = mdviewer.render('| A | B |\n|---|---|\n| 1 | 2 |\n\n```python\nprint("hola")\n```')
        self.assertIn('<table>', page)
        self.assertIn('class="highlight"', page)

    def test_html_is_text_and_unsafe_link_is_not_active(self):
        page = mdviewer.render('<script>alert(1)</script>\n\n[enlace](javascript:alert(1))')
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn('href="javascript:', page)

    def test_unique_heading_anchors(self):
        page = mdviewer.render('# Sección\n\n# Sección')
        self.assertIn('id="sección"', page)
        self.assertIn('id="sección-1"', page)

    def test_theme_and_relative_image(self):
        page = mdviewer.render('![Imagen](imagen.png)', dark=True)
        self.assertIn('class="dark"', page)
        self.assertIn('src="imagen.png"', page)
        self.assertIn("script-src 'none'", page)


if __name__ == '__main__':
    unittest.main()
