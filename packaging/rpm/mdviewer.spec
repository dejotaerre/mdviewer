Name:           mdviewer
Version:        0.1.1
Release:        1%{?dist}
Summary:        Visor Markdown de solo lectura para GNOME
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
%doc %{_docdir}/mdviewer/
%license %{_datadir}/licenses/mdviewer/LICENSE

%changelog
* Sat Oct 24 2026 Dejotaerre <126120344+dejotaerre@users.noreply.github.com> - 0.1.1-1
- Empaquetado inicial para Fedora.
