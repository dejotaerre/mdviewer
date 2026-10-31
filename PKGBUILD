pkgname=mdviewer
pkgver=0.2.0
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py' 'local.mdviewer.svg' 'background_io.py' 'file_worker.py' 'test_io.py' 'test_gui_io.py' 'test_edit.py')
sha256sums=('f0ccd8d65a566977417d9baf11f640d6bfc4d65609feccb79c051e6722dddba5'
            'a96c1d10e80d6d88c63faef155046ec901f20ea32a88654dc33e78fcf3c7d6e8'
            '542d4f3df99ea5399dc0abaa3cee8df8a5ed660d7ac3f62dd25b36818f0cb664'
            '39f82715ac134fe9315c7e6213f4a9f0b707e0401bbe6a137518b37568827056'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            'fae2c6f4d6c0fa288f53fcf55034f8cec62682c278546e22155deccffae681a1'
            '786e7351c10ae161e38cad4f76c5249117cfe6c90cdfe8817efa195df4661977'
            'e21406cce609998e54d0c5fb20bb5cd2d9b63e6d2f0f5bee5aadb8cfc312f2f2'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f'
            '09f205b7a29daf34a7eb2b147e8d23f9abeedeea253fee35c0e5014f071acaec'
            '5bf124a9b37f31e53c8d1e711dd691e33c0eb918ce95771057eda483d33d7f05'
            '3240622f0ab404bed3900c7ff3d679ae871b111dd01b76a52f29e443205a0e9d'
            '0683000148e8b42895bc7ad664b46ab3fd9995f2e447d1f960a175f7c07bf1ca'
            '705097b6463ad10b02f4e3812471f7915d3af6e895dc83b8d6b30dfe54622d15'
            'b41aa4d8cc7a6908bc165a0c38cef1c106e51c6d60d71e1021712ddca2734230')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
