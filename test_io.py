import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from gi.repository import GLib
from background_io import BackgroundJob
from file_worker import MAX_BYTES, read_document


class DocumentTests(unittest.TestCase):
    def test_utf8_bom_and_resolved_path(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'nota.MD'
            path.write_bytes(b'\xef\xbb\xbf# Hola')
            self.assertEqual(read_document(str(path)), {'path': str(path), 'source': '# Hola'})

    def test_reject_missing_invalid_large_and_special_files(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'nota.md'
            with self.assertRaises(OSError):
                read_document(str(path))
            path.write_bytes(b'\xff')
            with self.assertRaises(UnicodeError):
                read_document(str(path))
            with path.open('wb') as stream:
                stream.truncate(MAX_BYTES + 1)
            with self.assertRaises(ValueError):
                read_document(str(path))
            path.unlink()
            os.mkfifo(path)
            with self.assertRaises(ValueError):
                read_document(str(path))


class BackgroundTests(unittest.TestCase):
    def run_job(self, code, timeout=1000, cancel=False):
        loop = GLib.MainLoop()
        results, ticks = [], []
        def completed(result):
            results.append(result)
            loop.quit()
        job = BackgroundJob([sys.executable, '-c', code], timeout, completed)
        pulse = GLib.timeout_add(10, lambda: ticks.append(1) or True)
        deadline = GLib.timeout_add(4000, lambda: loop.quit() or False)
        if cancel:
            GLib.timeout_add(120, lambda: job.cancel() or False)
        loop.run()
        GLib.source_remove(pulse)
        GLib.source_remove(deadline)
        self.assertEqual(len(results), 1)
        return results[0], ticks, job

    def test_blocked_io_times_out_without_blocking_main_loop(self):
        with tempfile.TemporaryDirectory() as root:
            fifo = Path(root) / 'blocked'
            os.mkfifo(fifo)
            result, ticks, job = self.run_job(f'open({str(fifo)!r}).read()', timeout=150)
            self.assertEqual(result, {'timeout': True})
            self.assertGreater(len(ticks), 3)
            self.assertTrue(job.finished)

    def test_cancel_and_late_completion_are_ignored(self):
        result, ticks, job = self.run_job('import time; time.sleep(60)', cancel=True)
        self.assertEqual(result, {'cancelled': True})
        self.assertGreater(len(ticks), 3)
        job._finish({'path': '/resultado-tardio'})
        self.assertTrue(job.finished)

    def test_success_and_helper_failure(self):
        result, _, _ = self.run_job('print(\'{"path": "/tmp/nota.md"}\')')
        self.assertEqual(result['path'], '/tmp/nota.md')
        result, _, _ = self.run_job('raise SystemExit(1)')
        self.assertIn('error', result)
        result, _, _ = self.run_job('print("invalido")')
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
