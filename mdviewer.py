#!/usr/bin/python3
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, WebKit
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from background_io import BackgroundJob

ROOT = Path(__file__).resolve().parent


def render(source, dark=False):
    formatter = HtmlFormatter(style='monokai' if dark else 'friendly')

    def colorize(code, language, attrs):
        try:
            return highlight(code, get_lexer_by_name(language), formatter)
        except ClassNotFound:
            return '<pre><code>' + html.escape(code) + '</code></pre>'

    parser = MarkdownIt('commonmark', {'html': False, 'highlight': colorize})
    parser.enable(['table', 'strikethrough'])
    tokens = parser.parse(source)
    used = {}
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            slug = re.sub(r'[^\w\- ]', '', tokens[i + 1].content.lower()).replace(' ', '-') or 'seccion'
            number = used.get(slug, 0)
            used[slug] = number + 1
            token.attrSet('id', slug + (f'-{number}' if number else ''))
    body = parser.renderer.render(tokens, parser.options, {})
    css = (ROOT / 'style.css').read_text()
    return f'''<!doctype html><html lang="es" class="{'dark' if dark else 'light'}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src file: data:; style-src 'unsafe-inline'; script-src 'none'; base-uri 'none'; form-action 'none'">
<style>{css}\n{formatter.get_style_defs('.highlight')}</style>
</head><body><main>{body}</main></body></html>'''


class Window(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='mdviewer', default_width=1000, default_height=800)
        self.set_icon_name('local.mdviewer')
        self.job = None
        self.path = None
        self.source = ''
        self.saved_source = ''
        self.file_metadata = {}
        self.saving = False
        self.confirmation = None
        self.closing = False
        self.style = Adw.StyleManager.get_default()
        self.style_handler = self.style.connect('notify::dark', self.theme_changed)
        self.connect('close-request', self.on_close)
        self.overlay = Adw.ToastOverlay()
        layout = Adw.ToolbarView()
        self.set_content(self.overlay)
        self.overlay.set_child(layout)
        header = Adw.HeaderBar()
        self.heading = Adw.WindowTitle(title='mdviewer', subtitle='Un lugar tranquilo para leer Markdown')
        header.set_title_widget(self.heading)
        layout.add_top_bar(header)
        self.action('edit', self.toggle_editor, ['<Primary>e'])
        self.action('save', self.save_document, ['<Primary>s'])
        self.edit_button = Gtk.Button(label='Editar', tooltip_text='Editar / vista previa (Ctrl+E)', action_name='win.edit')
        header.pack_start(self.edit_button)
        header.pack_start(Gtk.Button(icon_name='document-save-symbolic', tooltip_text='Guardar (Ctrl+S)', action_name='win.save'))
        self.lookup_action('edit').set_enabled(False)
        self.lookup_action('save').set_enabled(False)
        self.action('open', self.choose_file, ['<Primary>o'])
        self.action('reload', self.reload_file, ['<Primary>r'])
        self.action('find', self.show_search, ['<Primary>f'])
        self.action('zoom-in', lambda: self.zoom(0.1), ['<Primary>plus', '<Primary>equal'])
        self.action('zoom-out', lambda: self.zoom(-0.1), ['<Primary>minus'])
        self.action('zoom-reset', lambda: self.web.set_zoom_level(1), ['<Primary>0'])
        self.action('close', self.close, ['<Primary>w'])
        header.pack_start(Gtk.Button(icon_name='document-open-symbolic', tooltip_text='Abrir archivo (Ctrl+O)', action_name='win.open'))
        header.pack_end(Gtk.Button(icon_name='system-search-symbolic', tooltip_text='Buscar (Ctrl+F)', action_name='win.find'))
        menu = Gio.Menu()
        for label, action in [('Acercar', 'zoom-in'), ('Alejar', 'zoom-out'), ('Tamaño original', 'zoom-reset'), ('Volver a cargar', 'reload')]:
            menu.append(label, 'win.' + action)
        header.pack_end(Gtk.MenuButton(icon_name='open-menu-symbolic', menu_model=menu))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        layout.set_content(box)
        self.search_bar = Gtk.SearchBar()
        search_box = Gtk.Box(spacing=6, margin_start=12, margin_end=12, margin_top=6, margin_bottom=6)
        self.search = Gtk.SearchEntry(hexpand=True, placeholder_text='Buscar en el documento…')
        self.search.connect('search-changed', self.find_text)
        self.search.connect('activate', lambda *_: self.web.get_find_controller().search_next())
        self.search.connect('stop-search', lambda *_: self.search_bar.set_search_mode(False))
        search_box.append(self.search)
        for icon, tip, callback in [('go-up-symbolic', 'Anterior', lambda *_: self.web.get_find_controller().search_previous()), ('go-down-symbolic', 'Siguiente', lambda *_: self.web.get_find_controller().search_next())]:
            button = Gtk.Button(icon_name=icon, tooltip_text=tip)
            button.connect('clicked', callback)
            search_box.append(button)
        self.search_bar.set_child(search_box)
        self.search_bar.connect_entry(self.search)
        self.search_bar.set_show_close_button(True)
        self.search_bar.connect('notify::search-mode-enabled', self.search_mode_changed)
        box.append(self.search_bar)
        self.stack = Gtk.Stack(vexpand=True)
        box.append(self.stack)
        welcome = Adw.StatusPage(title='mdviewer', description='Tus archivos Markdown, claros y cómodos de leer.\nAbre un archivo o arrástralo a esta ventana.', icon_name='local.mdviewer')
        button = Gtk.Button(label='Abrir archivo…', action_name='win.open', halign=Gtk.Align.CENTER)
        button.add_css_class('suggested-action')
        welcome.set_child(button)
        self.stack.add_named(welcome, 'welcome')
        self.web = WebKit.WebView()
        settings = self.web.get_settings()
        settings.set_enable_javascript(False)
        settings.set_allow_file_access_from_file_urls(True)
        settings.set_allow_universal_access_from_file_urls(False)
        self.web.connect('decide-policy', self.navigate)
        self.stack.add_named(self.web, 'document')
        self.editor = Gtk.TextView(monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR,
                                   left_margin=24, right_margin=24, top_margin=24, bottom_margin=24)
        self.buffer = self.editor.get_buffer()
        self.buffer.set_enable_undo(True)
        self.buffer.connect('changed', self.editor_changed)
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(self.editor)
        self.stack.add_named(scroll, 'editor')
        self.activity = Gtk.Box(spacing=12, margin_start=18, margin_end=18, margin_top=8, margin_bottom=8)
        self.activity_label = Gtk.Label(hexpand=True, xalign=0)
        self.activity.append(self.activity_label)
        cancel = Gtk.Button(label='Cancelar')
        cancel.connect('clicked', lambda *_: self.cancel_job())
        self.activity.append(cancel)
        self.activity.set_visible(False)
        box.append(self.activity)
        self.status = Gtk.Label(label='Solo lectura · Ctrl+O para abrir', xalign=0, margin_start=18, margin_end=18, margin_top=7, margin_bottom=7, ellipsize=3)
        self.status.add_css_class('dim-label')
        box.append(self.status)
        drop = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop.connect('drop', self.drop_files)
        self.add_controller(drop)

    def action(self, name, callback, shortcuts):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', lambda *_: callback())
        self.add_action(action)
        self.get_application().set_accels_for_action('win.' + name, shortcuts)

    def on_close(self, *_):
        if self.saving:
            self.toast('Espera a que termine el guardado o cancélalo antes de cerrar.')
            return True
        if self.dirty and not self.closing:
            self.confirm_discard(self.finish_close)
            return True
        self.cancel_job()
        self.style.disconnect(self.style_handler)
        return False

    @property
    def dirty(self):
        return self.source != self.saved_source

    def finish_close(self):
        self.closing = True
        self.close()

    def confirm_discard(self, continuation):
        if self.saving:
            self.toast('Espera a que termine el guardado o cancélalo.')
            return
        if not self.dirty:
            continuation()
            return
        if self.confirmation:
            self.confirmation.present()
            return
        dialog = Adw.MessageDialog(transient_for=self, modal=True,
                                  heading='¿Guardar los cambios?',
                                  body='El documento tiene cambios sin guardar.')
        self.confirmation = dialog
        dialog.add_response('cancel', 'Cancelar')
        dialog.add_response('discard', 'Descartar cambios')
        dialog.add_response('save', 'Guardar')
        dialog.set_response_appearance('discard', Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_response_appearance('save', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('save')
        dialog.set_close_response('cancel')
        def response(dialog, choice):
            self.confirmation = None
            if choice == 'discard':
                continuation()
            elif choice == 'save':
                self.save_document(continuation)
        dialog.connect('response', response)
        dialog.present()

    def update_document_state(self):
        if not self.path:
            return
        mark = '• ' if self.dirty else ''
        self.heading.set_title(mark + self.path.name)
        self.set_title(mark + self.path.name + ' — mdviewer')
        editing = self.stack.get_visible_child_name() == 'editor'
        self.edit_button.set_label('Vista previa' if editing else 'Editar')
        state = 'Cambios sin guardar' if self.dirty else ('Edición' if editing else 'Lectura')
        self.status.set_label(f'{state} · {len(self.source.split()):,} palabras · {self.path.name}')
        self.lookup_action('edit').set_enabled(not self.saving)
        self.lookup_action('save').set_enabled(self.dirty and not self.saving)

    def editor_changed(self, *_):
        if self.job and not self.saving:
            self.cancel_job()
        self.source = self.buffer.get_text(*self.buffer.get_bounds(), True)
        self.update_document_state()

    def toggle_editor(self):
        if not self.path or self.saving:
            return
        if self.stack.get_visible_child_name() == 'editor':
            self.display_document()
        else:
            self.cancel_job()
            self.search_bar.set_search_mode(False)
            self.stack.set_visible_child_name('editor')
            self.editor.grab_focus()
        self.update_document_state()

    def save_document(self, continuation=None):
        if not self.path or self.saving:
            return
        if not self.dirty:
            if continuation:
                continuation()
            return
        snapshot = self.source
        payload = dict(self.file_metadata, source=snapshot)
        self.cancel_job()
        self.saving = True
        self.editor.set_editable(False)
        self.update_document_state()
        def saved(result):
            self.saved_source = snapshot
            self.file_metadata['etag'] = result['etag']
            self.update_document_state()
            self.toast('Archivo guardado.')
            if continuation and not self.dirty:
                continuation()
        self.start_job('save', [str(self.path)], 'Guardando archivo…', 15000, saved,
                       input_text=json.dumps(payload), cancel_previous=False)

    def toast(self, message):
        self.overlay.add_toast(Adw.Toast(title=message))

    def cancel_job(self):
        was_saving = self.saving
        job, self.job = self.job, None
        if job:
            job.cancel()
        self.activity.set_visible(False)
        self.finish_saving()
        if was_saving:
            self.toast('Guardado sin confirmar. Conserva tus cambios y comprueba el archivo antes de reintentar.')

    def finish_saving(self):
        self.saving = False
        self.editor.set_editable(True)
        self.update_document_state()

    def start_job(self, mode, args, label, timeout_ms, callback, input_text=None, cancel_previous=True):
        if cancel_previous:
            self.cancel_job()
        self.activity_label.set_label(label)
        self.activity.set_visible(True)

        def completed(result):
            if self.job is not job:
                return
            self.job = None
            self.activity.set_visible(False)
            self.finish_saving()
            if mode == 'save' and (result.get('timeout') or result.get('cancelled')):
                self.toast('Guardado sin confirmar. Tus cambios siguen en el editor; comprueba el archivo antes de reintentar.')
                return
            if result.get('timeout'):
                self.toast('La operación tardó demasiado. La ubicación o el selector no responde.')
            elif result.get('error'):
                self.toast('No se pudo completar la operación: ' + result['error'])
            elif not result.get('cancelled'):
                callback(result)

        try:
            job = BackgroundJob(
                [sys.executable, str(ROOT / 'file_worker.py'), mode, *args],
                timeout_ms, completed, **({'input_text': input_text} if input_text is not None else {}))
            self.job = job
        except GLib.Error as error:
            self.activity.set_visible(False)
            self.finish_saving()
            self.toast('No se pudo iniciar la apertura: ' + error.message)

    def choose_file(self):
        self.confirm_discard(self.choose_file_confirmed)

    def choose_file_confirmed(self):
        self.start_job('choose', [], 'Selecciona un archivo…', 120000,
                       lambda result: self.open_file_confirmed(Gio.File.new_for_path(result['path'])))

    def open_file(self, file):
        self.confirm_discard(lambda: self.open_file_confirmed(file))

    def open_file_confirmed(self, file):
        name = file.get_path()
        if not name:
            self.toast('Selecciona un archivo local o montado.')
            return
        self.start_job('read', [name], 'Abriendo archivo…', 15000, self.document_loaded)

    def document_loaded(self, result):
        self.path = Path(result['path'])
        self.saved_source = result['source']
        self.file_metadata = {key: result[key] for key in ('etag', 'bom', 'newline')}
        self.buffer.set_enable_undo(False)
        self.buffer.set_text(result['source'])
        self.buffer.set_enable_undo(True)
        self.heading.set_title(self.path.name)
        self.heading.set_subtitle(str(self.path.parent))
        self.set_title(self.path.name + ' — mdviewer')
        self.status.set_label(f'Solo lectura · {len(self.source.split()):,} palabras · {self.path.name}')
        self.display_document()
        self.update_document_state()

    def display_document(self):
        self.web.load_html(render(self.source, self.style.get_dark()), self.path.as_uri())
        self.stack.set_visible_child_name('document')

    def theme_changed(self, *_):
        if self.path and self.stack.get_visible_child_name() != 'editor':
            self.display_document()

    def reload_file(self):
        if self.path:
            self.open_file(Gio.File.new_for_path(str(self.path)))

    def zoom(self, change):
        self.web.set_zoom_level(max(0.6, min(2.5, self.web.get_zoom_level() + change)))

    def show_search(self):
        if self.path:
            if self.stack.get_visible_child_name() == 'editor':
                self.display_document()
                self.update_document_state()
            self.search_bar.set_search_mode(True)
            self.search.grab_focus()

    def search_mode_changed(self, *_):
        if not self.search_bar.get_search_mode():
            self.web.get_find_controller().search_finish()
        else:
            self.find_text()

    def find_text(self, *_):
        text = self.search.get_text()
        controller = self.web.get_find_controller()
        if text:
            controller.search(text, WebKit.FindOptions.CASE_INSENSITIVE | WebKit.FindOptions.WRAP_AROUND, 10000)
        else:
            controller.search_finish()

    def drop_files(self, target, files, x, y):
        for file in files.get_files():
            self.open_file(file)
            break
        return True

    def navigate(self, web, decision, kind):
        if kind not in (WebKit.PolicyDecisionType.NAVIGATION_ACTION, WebKit.PolicyDecisionType.NEW_WINDOW_ACTION):
            return False
        navigation = decision.get_navigation_action()
        if navigation.get_navigation_type() != WebKit.NavigationType.LINK_CLICKED:
            return False
        uri = navigation.get_request().get_uri()
        parts = urlsplit(uri)
        if self.path and parts.scheme == 'file':
            path = Path(os.path.abspath(unquote(parts.path)))
            if path == self.path and parts.fragment:
                decision.use()
                return True
            decision.ignore()
            if path.suffix.lower() in ('.md', '.markdown'):
                self.open_file(Gio.File.new_for_path(str(path)))
            else:
                self.toast('Este enlace no apunta a un archivo Markdown.')
        else:
            decision.ignore()
            if parts.scheme in ('https', 'http', 'mailto'):
                Gtk.UriLauncher.new(uri).launch(self, None, self.link_opened)
        return True

    def link_opened(self, launcher, result):
        try:
            launcher.launch_finish(result)
        except GLib.Error:
            self.toast('No se pudo abrir el enlace.')


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id='local.mdviewer', flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_activate(self):
        window = self.get_active_window() or Window(self)
        window.present()

    def do_open(self, files, count, hint):
        for file in files:
            window = Window(self)
            window.open_file(file)
            window.present()


if __name__ == '__main__':
    sys.exit(Application().run(sys.argv))
