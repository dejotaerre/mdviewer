#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
output_dir="$PWD/dist"
mkdir -p "$output_dir"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM
version=$(sed -n 's/^Version: *//p' packaging/rpm/mdviewer.spec)
mkdir -p "$build_dir/SOURCES" "$build_dir/SPECS"
tar --exclude=.git --exclude=dist --exclude=src --exclude=pkg --exclude=__pycache__ --exclude='*.pkg.tar.*' --transform="s,^\.,mdviewer-$version," -czf "$build_dir/SOURCES/mdviewer-$version.tar.gz" .
rpmbuild --define "_topdir $build_dir" -ba packaging/rpm/mdviewer.spec
cp "$build_dir"/RPMS/noarch/*.rpm "$output_dir/"
cp "$build_dir"/SRPMS/*.rpm "$output_dir/"
