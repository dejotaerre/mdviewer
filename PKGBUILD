pkgname=mdviewer
pkgver=0.1.3
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py' 'local.mdviewer.svg')
sha256sums=('ba525e428c84e107eb0fd6fcb8f0ec76f13f29061f8c03de040fa4f8cb611bc9'
            'a96c1d10e80d6d88c63faef155046ec901f20ea32a88654dc33e78fcf3c7d6e8'
            'a94410b1a32bce2d99dafc53ee1d0d4b2d3d1affbe2c48b45f9d23177e6def22'
            'de156ab649adbce3b34d898dd6c7de8c1111dc029aa46e70aefeb0a016406b27'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            '833d5c66f53ace37a8b8567a1837673875967d7ebc01150ac5e35fef6b5c6d6f'
            '786e7351c10ae161e38cad4f76c5249117cfe6c90cdfe8817efa195df4661977'
            'e21406cce609998e54d0c5fb20bb5cd2d9b63e6d2f0f5bee5aadb8cfc312f2f2'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f'
            '09f205b7a29daf34a7eb2b147e8d23f9abeedeea253fee35c0e5014f071acaec')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
