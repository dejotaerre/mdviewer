import tempfile
import unittest
from pathlib import Path
from file_worker import read_document, save_document


class SaveTests(unittest.TestCase):
    def test_save_preserves_bom_crlf_permissions_and_backup(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'nota.md'
            original = b'\xef\xbb\xbf# Hola\r\nTexto\r\n'
            path.write_bytes(original)
            path.chmod(0o640)
            document = read_document(str(path))
            document['source'] = '# Editado\nNuevo\n'
            saved = save_document(str(path), document)
            self.assertTrue(saved['etag'])
            self.assertEqual(path.read_bytes(), b'\xef\xbb\xbf# Editado\r\nNuevo\r\n')
            self.assertEqual(Path(str(path) + '~').read_bytes(), original)
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)

    def test_external_change_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'nota.md'
            path.write_text('Original')
            document = read_document(str(path))
            path.write_text('Modificación externa con otro tamaño')
            document['source'] = 'Mi edición'
            with self.assertRaises(ValueError):
                save_document(str(path), document)
            self.assertEqual(path.read_text(), 'Modificación externa con otro tamaño')

    def test_deleted_file_is_not_recreated(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'nota.md'
            path.write_text('Original')
            document = read_document(str(path))
            path.unlink()
            with self.assertRaises(OSError):
                save_document(str(path), document)
            self.assertFalse(path.exists())
