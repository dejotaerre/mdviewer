pkgname=mdviewer
pkgver=0.1.0
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py')
sha256sums=('9a94d15c189c6683202d647568970f34b2ae555efab8f1c7be2dde29e80b0945'
            'a6151f29573b4bd0bf15961ef4f58a10fa7e81aa00a89ef7e10f90b0b695bc78'
            'a94410b1a32bce2d99dafc53ee1d0d4b2d3d1affbe2c48b45f9d23177e6def22'
            'c60562f3fcf71925712b38b893ef28ddb2f37c6fee3ac95450cb87ec1a141b8e'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            '198a365b5d0507fc436c68de3ef7a085883827b6969c1da0909d283c2f01d142'
            '9b33d816081655db88e1b601f5949887256f88d17223a65b5780a055901ae2e1'
            '574f78313861c7c96e1a35bf92971c169b8d032e72471253c92ad05d9b8a19ce'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
