#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
output_dir="$PWD/dist"
mkdir -p "$output_dir"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM
make DESTDIR="$build_dir" PREFIX=/usr install
install -Dm644 packaging/debian/control "$build_dir/DEBIAN/control"
install -Dm644 LICENSE "$build_dir/usr/share/doc/mdviewer/copyright"
install -Dm644 docs/capturas/claro.png "$build_dir/usr/share/doc/mdviewer/docs/capturas/claro.png"
install -Dm644 docs/capturas/oscuro.png "$build_dir/usr/share/doc/mdviewer/docs/capturas/oscuro.png"
size=$(du -sk "$build_dir/usr" | cut -f1)
printf 'Installed-Size: %s\n' "$size" >> "$build_dir/DEBIAN/control"
version=$(sed -n 's/^Version: //p' packaging/debian/control)
dpkg-deb --root-owner-group --build "$build_dir" "$output_dir/mdviewer_${version}_all.deb"
