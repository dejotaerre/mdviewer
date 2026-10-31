Name:           mdviewer
Version:        0.2.0
Release:        1%{?dist}
Summary:        Visor Markdown con edición opcional para GNOME
License:        MIT
URL:            https://github.com/dejotaerre/mdviewer
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  make
Requires:       python3
Requires:       python3-gobject
Requires:       gtk4 >= 4.10
Requires:       libadwaita >= 1.4
Requires:       webkitgtk6.0
Requires:       python3-markdown-it-py >= 3
Requires:       python3-pygments

%description
Visor nativo para GNOME con temas claro y oscuro, tablas, codigo
resaltado, imagenes locales, busqueda y zoom.

%prep
%autosetup

%build

%install
make DESTDIR=%{buildroot} PREFIX=%{_prefix} install
install -Dm644 docs/capturas/claro.png %{buildroot}%{_docdir}/mdviewer/docs/capturas/claro.png
install -Dm644 docs/capturas/oscuro.png %{buildroot}%{_docdir}/mdviewer/docs/capturas/oscuro.png

%files
%{_bindir}/mdviewer
%{_datadir}/mdviewer/
%{_datadir}/applications/local.mdviewer.desktop
%{_datadir}/icons/hicolor/scalable/apps/local.mdviewer.svg
%doc %{_docdir}/mdviewer/
%license %{_datadir}/licenses/mdviewer/LICENSE

%changelog
* Sat Oct 31 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.2.0-1
- Edicion opcional, vista previa y guardado protegido contra conflictos.

* Sat Oct 31 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.1.4-1
- Apertura cancelable en procesos aislados para evitar bloqueos por E/S remota.

* Sat Oct 24 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.1.3-1
- Icono propio integrado en GNOME.

* Sat Oct 24 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.1.2-1
- Colores adaptados a los temas claro y oscuro.

* Sat Oct 24 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.1.1-1
- Empaquetado inicial para Fedora.
