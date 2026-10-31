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
        cls.app = m.Adw.Application(application_id='local.mdviewer.Pruebas.' + cls.__name__, flags=m.Gio.ApplicationFlags.NON_UNIQUE)
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



@unittest.skipUnless(os.environ.get('MDVIEWER_GUI_TESTS') == '1', 'Requiere pantalla virtual')
class EditingTests(WindowIOTests):
    def tearDown(self):
        if self.window.confirmation:
            self.window.confirmation.response('cancel')
        self.window.saved_source = self.window.source
        super().tearDown()

    def edit(self):
        self.window.toggle_editor()
        self.window.buffer.set_text('# Texto editado\n\n**Nuevo contenido**')
        self.assertTrue(self.window.dirty)

    def test_edit_preview_save(self):
        self.edit()
        self.window.toggle_editor()
        self.assertEqual(self.window.stack.get_visible_child_name(), 'document')
        self.assertIn('Nuevo contenido', self.window.source)
        self.assertEqual(self.path.read_text(), '# Documento anterior')
        self.window.save_document()
        self.wait_for(lambda: self.window.job is None)
        self.assertFalse(self.window.dirty)
        self.assertEqual(self.path.read_text(), self.window.source)
        self.assertEqual(Path(str(self.path) + '~').read_text(), '# Documento anterior')

    def test_close_cancel_preserves_edits(self):
        self.edit()
        self.assertTrue(self.window.on_close())
        self.assertIsNotNone(self.window.confirmation)
        self.window.confirmation.response('cancel')
        self.assertTrue(self.window.dirty)
        self.assertFalse(self.window.closing)

    def test_open_requires_discard(self):
        self.edit()
        other = self.path.parent / 'otra.md'
        other.write_text('# Otra')
        self.window.open_file(m.Gio.File.new_for_path(str(other)))
        self.assertIsNotNone(self.window.confirmation)
        self.window.confirmation.response('cancel')
        self.assertEqual(self.window.path, self.path)
        self.window.open_file(m.Gio.File.new_for_path(str(other)))
        self.window.confirmation.response('discard')
        self.wait_for(lambda: self.window.job is None)
        self.assertEqual(self.window.path, other)
        self.assertFalse(self.window.dirty)

    def test_conflict_keeps_buffer_and_disk(self):
        self.edit()
        self.path.write_text('# Modificación externa')
        self.window.save_document()
        self.wait_for(lambda: self.window.job is None)
        self.assertTrue(self.window.dirty)
        self.assertEqual(self.path.read_text(), '# Modificación externa')
        self.assertIn('cambió fuera', self.messages[-1])
        self.assertTrue(self.window.editor.get_editable())

    def test_save_timeout_keeps_edits_and_reports_uncertainty(self):
        self.edit()
        def stalled(argv, timeout_ms, callback, **kwargs):
            return BackgroundJob([sys.executable, '-c', 'import time; time.sleep(60)'], 150, callback)
        with patch.object(m, 'BackgroundJob', stalled):
            self.window.save_document()
        self.assertTrue(self.window.saving)
        self.assertTrue(self.window.on_close())
        self.wait_for(lambda: self.window.job is None)
        self.assertTrue(self.window.dirty)
        self.assertIn('sin confirmar', self.messages[-1])
        self.assertEqual(self.path.read_text(), '# Documento anterior')
        self.assertTrue(self.window.editor.get_editable())


if __name__ == '__main__':
    unittest.main()
