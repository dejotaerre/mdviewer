#!/usr/bin/python3
import json
import stat
import sys
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024


def read_document(name):
    path = Path(name).resolve()
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Selecciona un archivo normal, no un directorio o dispositivo.')
    if info.st_size > MAX_BYTES:
        raise ValueError('El archivo supera el límite de 10 MB.')
    with path.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('El archivo supera el límite de 10 MB.')
    return {'path': str(path), 'source': data.decode('utf-8-sig')}


def choose_file():
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gio, GLib, Gtk
    GLib.set_prgname('mdviewer')
    GLib.set_application_name('mdviewer')
    Gtk.init()
    Gtk.Window.set_default_icon_name('local.mdviewer')
    loop = GLib.MainLoop()
    payload = {'cancelled': True}
    dialog = Gtk.FileDialog(title='Abrir Markdown — mdviewer', modal=False)
    filters = Gio.ListStore.new(Gtk.FileFilter)
    markdown = Gtk.FileFilter(name='Markdown (*.md, *.markdown)')
    for pattern in ['*.[mM][dD]', '*.[mM][aA][rR][kK][dD][oO][wW][nN]']:
        markdown.add_pattern(pattern)
    filters.append(markdown)
    everything = Gtk.FileFilter(name='Todos los archivos')
    everything.add_pattern('*')
    filters.append(everything)
    dialog.set_filters(filters)

    def selected(dialog, result):
        nonlocal payload
        try:
            file = dialog.open_finish(result)
            name = file.get_path()
            payload = {'path': name} if name else {'error': 'Selecciona un archivo local o montado.'}
        except GLib.Error as error:
            if not error.matches(Gtk.DialogError.quark(), Gtk.DialogError.DISMISSED):
                payload = {'error': error.message}
        loop.quit()

    dialog.open(None, None, selected)
    loop.run()
    return payload


if __name__ == '__main__':
    try:
        result = choose_file() if sys.argv[1] == 'choose' else read_document(sys.argv[2])
    except (OSError, UnicodeError, ValueError) as error:
        result = {'error': str(error)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
