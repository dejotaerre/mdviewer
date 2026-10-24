# Empaquetado

Los tres formatos usan los mismos fuentes y el mismo lanzador Python 3.

- Arch/CachyOS: `makepkg -si` desde la raíz.
- Debian/Ubuntu: `./packaging/build-deb.sh`, con `make` y `dpkg-dev`.
- Fedora: `./packaging/build-rpm.sh`, con `make` y `rpm-build`.

Los scripts DEB/RPM no requieren privilegios de administrador para construir. La instalación sí requiere privilegios y debe hacerse con `apt install ./archivo.deb`, `dnf install ./archivo.rpm` o `pacman -U archivo.pkg.tar.zst`, para resolver dependencias.

## Dependencias

| Componente | Debian/Ubuntu | Fedora |
| --- | --- | --- |
| Python | python3 | python3 |
| PyGObject | python3-gi | python3-gobject |
| GTK 4.10+ | gir1.2-gtk-4.0 | gtk4 |
| libadwaita 1.4+ | gir1.2-adw-1 | libadwaita |
| WebKitGTK 6 | gir1.2-webkit-6.0 | webkitgtk6.0 |
| Markdown | python3-markdown-it | python3-markdown-it-py |
| Resaltado | python3-pygments | python3-pygments |

Los nombres se verifican contra los repositorios de cada distribución. Consulta también las fichas de [Markdown para Debian](https://packages.debian.org/trixie/python3-markdown-it) y [Markdown para Fedora](https://packages.fedoraproject.org/pkgs/python-markdown-it-py/python3-markdown-it-py/).

## Validación antes de publicar

1. Construir los paquetes desde una copia de los fuentes sin cambios pendientes ajenos a la versión.
2. Instalarlos con resolución de dependencias en contenedores limpios de las distribuciones objetivo.
3. Ejecutar `make check PYTHON=python3` y comprobar que la aplicación instalada puede crear una ventana y cargar un documento con WebKit en una pantalla virtual.
4. Comprobar el comando `mdviewer --help`, los metadatos y las dependencias del paquete.
5. Publicar los paquetes junto con sus sumas SHA-256.

Las pruebas de pantalla virtual comprueban el arranque y la carga de documentos, pero no sustituyen la revisión visual y de integración en una sesión GNOME real. El escritorio de CachyOS es el entorno de revisión visual.

## Nueva versión

Actualizar la versión en `PKGBUILD`, `packaging/debian/control` y `packaging/rpm/mdviewer.spec`. Actualizar las instrucciones del README y los checksums de `PKGBUILD`; regenerar `.SRCINFO` con `makepkg --printsrcinfo`.

No reemplazar silenciosamente los archivos de una versión ya publicada: publicar una versión nueva si cambia el programa o sus paquetes.
