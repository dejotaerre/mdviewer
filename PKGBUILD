pkgname=mdviewer
pkgver=0.1.2
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py')
sha256sums=('cbf579a259f222da9377844b8196d469f09fabc3a698f0f7cdf7787bba5e6e0b'
            'a96c1d10e80d6d88c63faef155046ec901f20ea32a88654dc33e78fcf3c7d6e8'
            'a94410b1a32bce2d99dafc53ee1d0d4b2d3d1affbe2c48b45f9d23177e6def22'
            '80a46689170ba24c803777bebdbfe6de3893d3cf444d61e7e89f5c604f7355a3'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            'b003a0de168c2f5a284838a25e15f6e9dae4fbe304de9b54ad6aea53d2805ecb'
            '9b33d816081655db88e1b601f5949887256f88d17223a65b5780a055901ae2e1'
            'e21406cce609998e54d0c5fb20bb5cd2d9b63e6d2f0f5bee5aadb8cfc312f2f2'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
