pkgname=mdviewer
pkgver=0.1.4
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py' 'local.mdviewer.svg' 'background_io.py' 'file_worker.py' 'test_io.py' 'test_gui_io.py')
sha256sums=('16f9b2b406deb689dcd05ec9a62f49ed5070c78ed8ba86ea858e842f572b2701'
            'a96c1d10e80d6d88c63faef155046ec901f20ea32a88654dc33e78fcf3c7d6e8'
            'a94410b1a32bce2d99dafc53ee1d0d4b2d3d1affbe2c48b45f9d23177e6def22'
            'e7926e4fbbbd34b1fbceb6066772720b1f3c0ade50111bc4d036ed595f2ef9fb'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            'fae2c6f4d6c0fa288f53fcf55034f8cec62682c278546e22155deccffae681a1'
            '786e7351c10ae161e38cad4f76c5249117cfe6c90cdfe8817efa195df4661977'
            'e21406cce609998e54d0c5fb20bb5cd2d9b63e6d2f0f5bee5aadb8cfc312f2f2'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f'
            '09f205b7a29daf34a7eb2b147e8d23f9abeedeea253fee35c0e5014f071acaec'
            'fadd0ae1ff630c78e72d7aba28030fa95b64e25bdf1a504223ecb85cfda0d805'
            '6bbbb37b6bb64d4019bf1fbaa66c9c228f920f4187060264a23672145a101797'
            '0da4e4ef800c38a30da0d671f6a7dc8f0dfb50b07d90cc05ce27cfdff59338ea'
            '8683aae44eeab755c2c321731db75f4434e889e21ada630b0f8d52c6d0d52dd3')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
