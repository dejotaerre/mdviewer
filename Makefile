PREFIX ?= /usr
PYTHON ?= python3

.PHONY: install check
install:
	install -Dm755 mdviewer $(DESTDIR)$(PREFIX)/bin/mdviewer
	install -Dm644 mdviewer.py $(DESTDIR)$(PREFIX)/share/mdviewer/mdviewer.py
	install -Dm644 local.mdviewer.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/local.mdviewer.svg
	install -Dm644 style.css $(DESTDIR)$(PREFIX)/share/mdviewer/style.css
	install -Dm644 BIENVENIDA.md $(DESTDIR)$(PREFIX)/share/mdviewer/BIENVENIDA.md
	install -Dm644 local.mdviewer.desktop $(DESTDIR)$(PREFIX)/share/applications/local.mdviewer.desktop
	install -Dm644 README.md $(DESTDIR)$(PREFIX)/share/doc/mdviewer/README.md
	install -Dm644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/mdviewer/LICENSE

check:
	$(PYTHON) -m unittest discover -v
	desktop-file-validate local.mdviewer.desktop
