# mdviewer

Un visor Markdown de solo lectura para GNOME. Interfaz nativa con GTK 4 y libadwaita, tipografía cómoda y tema claro u oscuro según las preferencias del escritorio.

## Funciones

- Apertura de archivos, arrastrar y soltar y varias ventanas.
- Tablas, listas, citas, tachado y código resaltado con Pygments.
- Imágenes locales y enlaces entre documentos Markdown.
- Búsqueda dentro del documento, zoom y recarga manual.
- Integración con «Abrir con» en el gestor de archivos.
- Enlaces web abiertos en el navegador del sistema.

## Instalar en CachyOS o Arch Linux

Con `base-devel` y Git instalados:

```sh
git clone https://github.com/dejotaerre/mdviewer.git
cd mdviewer
makepkg -si
```

El paquete se instala para todos los usuarios. Las dependencias se resuelven mediante los repositorios nativos: `python`, `python-gobject`, `gtk4`, `libadwaita`, `webkitgtk-6.0`, `python-markdown-it-py` y `python-pygments`.

Para instalar un paquete ya construido:

```sh
sudo pacman -U ./mdviewer-*.pkg.tar.zst
```

Para desinstalar:

```sh
sudo pacman -R mdviewer
```

## Uso

Busca **mdviewer** en el menú de aplicaciones o ejecuta:

```sh
mdviewer documento.md
```

| Acción | Atajo |
| --- | --- |
| Abrir | Ctrl+O |
| Buscar | Ctrl+F |
| Siguiente coincidencia | Enter en el buscador |
| Acercar / alejar | Ctrl++ / Ctrl+- |
| Tamaño original | Ctrl+0 |
| Volver a cargar | Ctrl+R |
| Cerrar ventana | Ctrl+W |

Para abrir `.md`, `.MD` y `.markdown` con doble clic, cada usuario puede elegir mdviewer como aplicación predeterminada o ejecutar:

```sh
gio mime text/markdown local.mdviewer.desktop
gio mime text/x-markdown local.mdviewer.desktop
```

La instalación no impone asociaciones a otros usuarios.

## Desarrollo

Con las dependencias instaladas:

```sh
python mdviewer.py BIENVENIDA.md
make check
```

La aplicación busca `style.css` junto a `mdviewer.py`, por lo que funciona directamente desde el repositorio. El lanzador del paquete usa `/usr/share/mdviewer/`. La instalación soportada utiliza el prefijo `/usr`.

## Alcance de esta versión

Acepta archivos locales UTF-8, con o sin BOM, hasta 10 MB. No modifica los documentos. Las imágenes remotas no se descargan; el HTML incrustado se muestra como texto y JavaScript está desactivado. Los diagramas Mermaid se muestran como código; no hay renderizado de fórmulas matemáticas ni recarga automática.

El cambio de tema vuelve a cargar el documento y puede reiniciar la posición de lectura.

## Créditos

Creado por Dejotaerre. Construido con Python, GTK, libadwaita, WebKitGTK, markdown-it-py y Pygments.
