import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mdviewer as m
from background_io import BackgroundJob


@unittest.skipUnless(os.environ.get('MDVIEWER_GUI_TESTS') == '1', 'Requiere pantalla virtual')
class WindowIOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = m.Adw.Application(application_id='local.mdviewer.Pruebas', flags=m.Gio.ApplicationFlags.NON_UNIQUE)
        cls.app.register(None)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'nota.md'
        self.path.write_text('# Documento anterior')
        self.window = m.Window(self.app)
        self.window.present()
        self.messages = []
        self.window.toast = self.messages.append
        self.window.open_file(m.Gio.File.new_for_path(str(self.path)))
        self.wait_for(lambda: self.window.job is None)
        self.assertEqual(self.window.path, self.path)

    def tearDown(self):
        self.window.close()
        self.directory.cleanup()

    def wait_for(self, condition):
        loop = m.GLib.MainLoop()
        def check():
            if condition():
                loop.quit()
            return True
        poll = m.GLib.timeout_add(10, check)
        deadline = m.GLib.timeout_add(4000, lambda: loop.quit() or False)
        loop.run()
        m.GLib.source_remove(poll)
        m.GLib.source_remove(deadline)
        self.assertTrue(condition())

    def stalled(self, argv, timeout_ms, callback):
        return BackgroundJob([sys.executable, '-c', 'import time; time.sleep(60)'], 150, callback)

    def test_stalled_selector_times_out_and_window_still_works(self):
        with patch.object(m, 'BackgroundJob', self.stalled):
            self.window.choose_file()
        self.window.zoom(0.1)
        self.assertGreater(self.window.web.get_zoom_level(), 1)
        self.wait_for(lambda: self.window.job is None)
        self.assertIn('tardó demasiado', self.messages[-1])
        self.assertEqual(self.window.path, self.path)
        self.window.reload_file()
        self.wait_for(lambda: self.window.job is None)
        self.assertEqual(self.window.source, '# Documento anterior')

    def test_cancel_read_preserves_document_and_next_read_works(self):
        with patch.object(m, 'BackgroundJob', self.stalled):
            self.window.open_file(m.Gio.File.new_for_path('/ubicacion/inaccesible.md'))
        stale = self.window.job
        self.window.cancel_job()
        self.assertIsNone(self.window.job)
        self.assertFalse(self.window.activity.get_visible())
        self.assertEqual(self.window.path, self.path)
        self.path.write_text('# Nuevo documento')
        self.window.reload_file()
        self.wait_for(lambda: self.window.job is None)
        stale.callback({'path': '/resultado-tardio', 'source': 'obsoleto'})
        self.assertEqual(self.window.source, '# Nuevo documento')

    def test_missing_file_preserves_document(self):
        self.window.open_file(m.Gio.File.new_for_path(str(self.path.parent / 'ausente.md')))
        self.wait_for(lambda: self.window.job is None)
        self.assertTrue(self.messages)
        self.assertEqual(self.window.path, self.path)


if __name__ == '__main__':
    unittest.main()
