pkgname=mdviewer
pkgver=0.2.1
pkgrel=1
pkgdesc='Visor Markdown nativo para GNOME con búsqueda, zoom y resaltado de código'
arch=('any')
url='https://github.com/dejotaerre/mdviewer'
license=('MIT')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'webkitgtk-6.0' 'python-markdown-it-py' 'python-pygments')
checkdepends=('desktop-file-utils')
source=('mdviewer.py' 'style.css' 'BIENVENIDA.md' 'README.md' 'LICENSE' 'Makefile' 'local.mdviewer.desktop' 'mdviewer' 'test_render.py' 'local.mdviewer.svg' 'background_io.py' 'file_worker.py' 'test_io.py' 'test_gui_io.py' 'test_edit.py')
sha256sums=('a3631180b23bcd12bdf7a7860a0cc95151852fee2bce84eab97db86212862c68'
            'a96c1d10e80d6d88c63faef155046ec901f20ea32a88654dc33e78fcf3c7d6e8'
            '49c867975ee9e7e1e98d2be1c751596a511f739e33a21ecfde878ea333904680'
            'fda2f967e87083f85213b419f7413e5c5126cbc49c9e8959f34ebfcf7859f7aa'
            '87471d3877b658391f6e1f0af3d3ed744165ea0eabf7a2adf1c49450e9369336'
            'fae2c6f4d6c0fa288f53fcf55034f8cec62682c278546e22155deccffae681a1'
            '786e7351c10ae161e38cad4f76c5249117cfe6c90cdfe8817efa195df4661977'
            'e21406cce609998e54d0c5fb20bb5cd2d9b63e6d2f0f5bee5aadb8cfc312f2f2'
            '898e8206b501218ef13c0283575668ed0954c89ef3358e7de5f659f6ea8da97f'
            '09f205b7a29daf34a7eb2b147e8d23f9abeedeea253fee35c0e5014f071acaec'
            '5bf124a9b37f31e53c8d1e711dd691e33c0eb918ce95771057eda483d33d7f05'
            '314b6367529d181ee93ea255ac0ef17f801b42aab11a040e6b23d58328419df8'
            '0683000148e8b42895bc7ad664b46ab3fd9995f2e447d1f960a175f7c07bf1ca'
            'a25f13a72d6bf5f9611975b9e9262c07a3baabe8a2b22c22ee8306e808bd2874'
            'e16fb0112cba9c4fd3f741a724dbc4224cee7e0e8309273335ed18c4e229a158')

check() {
    make check
}

package() {
    make DESTDIR="$pkgdir" PREFIX=/usr install
}
