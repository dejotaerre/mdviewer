#!/usr/bin/python3
import json
import stat
import sys
from pathlib import Path
from gi.repository import Gio, GLib

MAX_BYTES = 10 * 1024 * 1024


def read_document(name):
    path = Path(name).resolve()
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Selecciona un archivo normal, no un directorio o dispositivo.')
    if info.st_size > MAX_BYTES:
        raise ValueError('El archivo supera el límite de 10 MB.')
    file = Gio.File.new_for_path(str(path))
    etag = file.query_info('etag::value', Gio.FileQueryInfoFlags.NONE, None).get_etag()
    with path.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('El archivo supera el límite de 10 MB.')
    current = file.query_info('etag::value', Gio.FileQueryInfoFlags.NONE, None).get_etag()
    if not etag or etag != current:
        raise ValueError('El archivo cambió durante la lectura. Vuelve a abrirlo.')
    text = data.decode('utf-8-sig')
    newline = '\r\n' if '\r\n' in text and text.count('\n') == text.count('\r\n') else '\n'
    return {'path': str(path), 'source': text.replace('\r\n', '\n'),
            'etag': etag, 'bom': data.startswith(b'\xef\xbb\xbf'), 'newline': newline}


def document_bytes(payload):
    data = payload['source'].replace('\n', payload.get('newline', '\n')).encode('utf-8')
    if payload.get('bom'):
        data = b'\xef\xbb\xbf' + data
    if len(data) > MAX_BYTES:
        raise ValueError('El documento supera el límite de 10 MB.')
    return data


def save_copy(name, payload):
    data = document_bytes(payload)
    path = Path(name).absolute()
    # La creación exclusiva rechaza destinos existentes, incluidos enlaces al original.
    with path.open('xb') as stream:
        stream.write(data)
    etag = Gio.File.new_for_path(str(path)).query_info('etag::value', Gio.FileQueryInfoFlags.NONE, None).get_etag()
    return {'path': str(path), 'etag': etag}


def save_document(name, payload):
    path = Path(name)
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('El destino ya no es un archivo normal.')
    file = Gio.File.new_for_path(str(path))
    etag = payload['etag']
    if not etag:
        raise ValueError('Vuelve a abrir el archivo antes de guardarlo.')
    data = document_bytes(payload)
    try:
        _, new_etag = file.replace_contents(data, etag, True, Gio.FileCreateFlags.NONE, None)
    except GLib.Error as error:
        if error.matches(Gio.io_error_quark(), Gio.IOErrorEnum.WRONG_ETAG):
            raise ValueError('El archivo cambió fuera de mdviewer. No se sobrescribió; conserva tus cambios antes de recargar.') from error
        raise
    return {'etag': new_etag}



def choose_file(save_name=None):
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gio, GLib, Gtk
    GLib.set_prgname('mdviewer')
    GLib.set_application_name('mdviewer')
    Gtk.init()
    Gtk.Window.set_default_icon_name('local.mdviewer')
    loop = GLib.MainLoop()
    payload = {'cancelled': True}
    dialog = Gtk.FileDialog(title='Guardar como — mdviewer' if save_name else 'Abrir Markdown — mdviewer', modal=False)
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
            file = dialog.save_finish(result) if save_name else dialog.open_finish(result)
            name = file.get_path()
            payload = {'path': name} if name else {'error': 'Selecciona un archivo local o montado.'}
        except GLib.Error as error:
            if not error.matches(Gtk.DialogError.quark(), Gtk.DialogError.DISMISSED):
                payload = {'error': error.message}
        loop.quit()

    if save_name:
        dialog.set_initial_name(save_name)
        dialog.save(None, None, selected)
    else:
        dialog.open(None, None, selected)
    loop.run()
    return payload


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'choose':
            result = choose_file()
        elif sys.argv[1] == 'choose-save':
            result = choose_file(sys.argv[2])
        elif sys.argv[1] == 'save-copy':
            result = save_copy(sys.argv[2], json.load(sys.stdin))
        elif sys.argv[1] == 'save':
            result = save_document(sys.argv[2], json.load(sys.stdin))
        else:
            result = read_document(sys.argv[2])
    except (OSError, UnicodeError, ValueError, GLib.Error) as error:
        result = {'error': str(error)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
