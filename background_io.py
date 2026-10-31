import json
from gi.repository import Gio, GLib


class BackgroundJob:
    """Aísla operaciones bloqueantes sin esperar su salida en el hilo gráfico."""

    def __init__(self, argv, timeout_ms, callback, input_text=None):
        self.callback = callback
        self.finished = False
        self.cancellable = Gio.Cancellable()
        self.process = Gio.Subprocess.new(argv, Gio.SubprocessFlags.STDOUT_PIPE | (Gio.SubprocessFlags.STDIN_PIPE if input_text is not None else Gio.SubprocessFlags.NONE))
        self.timer = GLib.timeout_add(timeout_ms, self._timeout)
        self.process.communicate_utf8_async(input_text, self.cancellable, self._completed)

    def _finish(self, result):
        if self.finished:
            return
        self.finished = True
        if self.timer:
            GLib.source_remove(self.timer)
            self.timer = None
        self.callback(result)

    def _completed(self, process, result):
        try:
            _, output, _ = process.communicate_utf8_finish(result)
            if self.finished:
                return
            if not process.get_successful():
                raise ValueError('El proceso de apertura terminó inesperadamente.')
            payload = json.loads(output)
            if not isinstance(payload, dict):
                raise ValueError('Respuesta de apertura inválida.')
        except (GLib.Error, ValueError) as error:
            payload = {'error': str(error)}
        self._finish(payload)

    def cancel(self, timeout=False):
        if self.finished:
            return
        # Nunca esperar al proceso: el núcleo puede retenerlo por una E/S remota.
        self.process.force_exit()
        self.cancellable.cancel()
        self._finish({'timeout': True} if timeout else {'cancelled': True})

    def _timeout(self):
        self.timer = None
        self.cancel(timeout=True)
        return GLib.SOURCE_REMOVE
